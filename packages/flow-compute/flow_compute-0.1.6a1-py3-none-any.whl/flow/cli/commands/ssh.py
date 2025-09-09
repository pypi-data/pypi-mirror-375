"""SSH command for connecting to running GPU instances.

Provides secure shell access to running tasks for debugging and development.
Keep examples in CLI help to avoid drift.
"""

import logging
import os
import shlex
import subprocess
from contextlib import suppress

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.ui.formatters import TaskFormatter
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.task_selector_mixin import TaskFilter, TaskOperationCommand
from flow.errors import FlowError
from flow.plugins import registry as plugin_registry

# Back-compat: expose Flow for tests that patch flow.cli.commands.ssh.Flow
# Export Flow for test-time monkeypatching of flow.cli.commands.ssh.Flow
from flow.sdk.client import Flow  # noqa: F401
from flow.sdk.models import Task


class SSHCommand(BaseCommand, TaskOperationCommand):
    """SSH command implementation.

    Handles both interactive sessions and remote command execution.
    Requires task to be in running state with SSH keys configured.
    """

    def __init__(self):
        """Initialize command with formatter."""
        super().__init__()
        self.task_formatter = TaskFormatter()

    @property
    def name(self) -> str:
        return "ssh"

    @property
    def manages_own_progress(self) -> bool:
        """SSH manages its own progress display."""
        return True

    @property
    def help(self) -> str:
        return """SSH to running GPU instances - Interactive shell or remote command execution

Quick connect:
  flow ssh                         # Interactive task selector
  flow ssh my-training             # Connect by task name
  flow ssh abc-123                 # Connect by task ID

Remote commands:
  flow ssh task -- nvidia-smi      # Run command remotely (after --)
  flow ssh task -- htop            # Monitor system resources
  flow ssh task --node 0           # Connect to specific node (0-based)

Tip: Use verbose help for container mode and advanced examples (flow ssh --verbose)."""

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Show running tasks; SSH may still be provisioning.

        We purposely allow tasks without an SSH endpoint yet so users can
        select a running task and the command will wait for SSH readiness.
        """
        return TaskFilter.running_only

    def get_selection_title(self) -> str:
        return "Select a running task to SSH into"

    def get_no_tasks_message(self) -> str:
        return "No running tasks available for SSH"

    # Command execution
    def execute_on_task(self, task: Task, client, **kwargs) -> None:
        """Execute SSH connection on the selected task with a unified timeline."""
        command = kwargs.get("command")
        node = kwargs.get("node", 0)
        record = kwargs.get("record", False)
        fast_flag = bool(kwargs.get("fast", False))

        # Validate node parameter for multi-instance tasks (shared helper)
        from flow.cli.utils.task_utils import (
            validate_node_index,  # local import to avoid CLI cold-start cost
        )

        validate_node_index(task, node)

        # Optional fast-mode from CLI flag
        if fast_flag:
            try:
                os.environ["FLOW_SSH_FAST"] = "1"
            except Exception:
                pass

        # Cache-first direct exec for the common case: interactive, not recording, node 0
        try:
            if self._try_direct_exec_from_cache(
                task, client, node=node, command=command, record=record
            ):
                return
        except Exception:
            pass

        # Unified timeline
        from flow.cli.utils.step_progress import StepTimeline  # local import by design

        timeline = StepTimeline(console, title="flow ssh", title_animation="auto")
        timeline.start()
        finished = False
        try:
            self._ensure_provider_support(client)
            self._ensure_default_ssh_key(client)
            task = self._maybe_wait_for_ssh(task, client, timeline)
            task = self._refresh_task(client, task)
            task = self._resolve_endpoint(client, task, node)
            self._maybe_wait_handshake(client, task, timeline)

            # Finish before handing control to the user's terminal/output
            if command:
                idx = timeline.add_step("Executing remote command", show_bar=False)
                timeline.start_step(idx)
                timeline.complete_step()
                timeline.finish()
                finished = True
                self._connect(task, client, command, node, record)
            else:
                timeline.finish()
                finished = True
                self._connect(task, client, None, node, record)

            self._maybe_print_next_actions(task, ran_command=bool(command))
        except Exception as e:
            self._handle_connect_error(e, client, task, timeline)
            raise
        finally:
            if not finished:
                timeline.finish()

    # ----- Cohesive helpers (extracted for testability) -----
    def _ensure_provider_support(self, client) -> None:
        """Ensure the current provider supports remote operations, else guide the user.

        Uses a lightweight capability probe and raises a ClickException if unsupported.
        """
        try:
            _ = client.get_remote_operations()
        except (AttributeError, NotImplementedError):
            from flow.cli.utils.provider_support import print_provider_not_supported

            print_provider_not_supported(
                "remote operations",
                tips=[
                    "Try again after switching provider: [accent]flow init --provider mithril[/accent]",
                    "Open a shell via the provider UI if available",
                ],
            )
            raise click.ClickException("Provider does not support remote operations")

    def _ensure_default_ssh_key(self, client) -> None:
        """Best-effort default SSH key creation; logs at debug on failure.

        Avoids silent hangs where instances never expose SSH due to missing keys.
        """
        log = logging.getLogger(__name__)
        try:
            from flow.cli.utils.ssh_launch_keys import (
                ensure_default_project_ssh_key as _ensure,
            )

            _ensure(client)
        except Exception as e:
            # Best-effort: log only at debug
            try:
                log.debug("ensure_default_ssh_key failed: %s", e)
            except Exception:
                pass

    def _maybe_wait_for_ssh(self, task: Task, client, timeline):
        """Wait for SSH details only when needed, with accurate messaging.

        - If the task is already RUNNING but lacks an endpoint, show a short
          "Resolving SSH endpoint" step instead of a long "Provisioning" step.
        - Fall back to the longer provisioning message only when the task
          truly looks like it's still starting.
        """
        if self._is_fast_mode() or getattr(task, "ssh_host", None):
            return task

        from flow.cli.utils.step_progress import (  # local import
            SSHWaitProgressAdapter,
            build_provisioning_hint,
            build_wait_hints,
        )
        from flow.sdk.ssh_utils import DEFAULT_PROVISION_MINUTES, SSHNotReadyError

        try:
            from flow.sdk.models import TaskStatus as _TaskStatus  # local import
        except Exception:
            _TaskStatus = None  # type: ignore[assignment]

        # Determine copy and timeout based on current state/age
        try:
            baseline = int(getattr(task, "instance_age_seconds", 0) or 0)
        except (TypeError, ValueError):
            baseline = 0

        is_running = False
        try:
            if _TaskStatus is not None:
                is_running = getattr(task, "status", None) == getattr(_TaskStatus, "RUNNING", None)
            else:
                is_running = str(getattr(task, "status", "")).lower() == "running"
        except Exception:
            is_running = False

        # Shorter resolve window for running tasks; otherwise use provisioning budget
        if is_running or baseline >= 60:
            step_label = "Resolving SSH endpoint"
            estimated_seconds = int(os.getenv("FLOW_SSH_RESOLVE_TIMEOUT", "180"))
            hint = build_wait_hints("SSH", "flow ssh")
        else:
            step_label = f"Provisioning instance (up to {DEFAULT_PROVISION_MINUTES}m)"
            estimated_seconds = DEFAULT_PROVISION_MINUTES * 60
            hint = build_provisioning_hint("instance", "flow ssh")

        step_idx = timeline.add_step(
            step_label,
            show_bar=True,
            estimated_seconds=estimated_seconds,
            baseline_elapsed_seconds=baseline,
        )
        adapter = SSHWaitProgressAdapter(
            timeline,
            step_idx,
            estimated_seconds,
            baseline_elapsed_seconds=baseline,
        )
        try:
            with adapter:
                timeline.set_active_hint_text(hint)
                return client.wait_for_ssh(
                    task_id=task.task_id,
                    timeout=estimated_seconds,
                    show_progress=False,
                    progress_adapter=adapter,
                )
        except SSHNotReadyError as e:
            timeline.fail_step(str(e))
            raise SystemExit(1)

    def _refresh_task(self, client, task: Task) -> Task:
        """Fetch a fresh view of the task if possible."""
        with suppress(FlowError):
            return client.get_task(task.task_id)
        return task

    def _resolve_endpoint(self, client, task: Task, node: int) -> Task:
        """Resolve the freshest SSH endpoint for the given task/node, best-effort."""
        # Short-circuit to avoid network calls when endpoint is already present
        if getattr(task, "ssh_host", None) and getattr(task, "ssh_port", None):
            return task
        try:
            host, port = client.resolve_ssh_endpoint(task.task_id, node=node)
            task.ssh_host = host
            task.ssh_port = int(port or 22)
        except (FlowError, ValueError, AttributeError):
            pass
        return task

    def _maybe_wait_handshake(self, client, task: Task, timeline) -> None:
        """Wait for SSH handshake; fail fast if it never becomes ready.

        Previously, we would continue even when the handshake never succeeded,
        which could lead to an indefinite hang in the interactive ssh process
        (e.g., TCP open on a bastion/load-balancer that never completes SSH).
        Now we surface a clear, bounded failure with suggestions.
        """
        if self._is_fast_mode() or not getattr(task, "ssh_host", None):
            return
        try:
            ssh_key_path, _ = client.get_task_ssh_connection_info(task.task_id)
        except FlowError:
            ssh_key_path = None
        import time as _t

        from flow.cli.utils.ssh_helpers import SshStack as _S
        from flow.cli.utils.step_progress import SSHWaitProgressAdapter  # local import

        handshake_seconds = int(os.getenv("FLOW_SSH_HANDSHAKE_SEC", "90"))
        step_idx = timeline.add_step(
            "Establishing SSH session", show_bar=True, estimated_seconds=handshake_seconds
        )
        adapter = SSHWaitProgressAdapter(timeline, step_idx, handshake_seconds)
        with adapter:
            start_wait = _t.time()
            # Include ProxyJump for readiness checks when provider supplies it
            try:
                pj = (getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump")
                pfx = ["-J", str(pj)] if pj else None
            except Exception:
                pfx = None
            while True:
                # If we have a key, do a full BatchMode probe; otherwise check SSH banner only
                if ssh_key_path and _S.is_ssh_ready(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=task.ssh_host,
                    port=getattr(task, "ssh_port", 22),
                    key_path=ssh_key_path,
                    prefix_args=pfx,
                ):
                    break
                if not ssh_key_path and _S.tcp_port_open(
                    task.ssh_host, int(getattr(task, "ssh_port", 22))
                ):
                    try:
                        # Banner check avoids false-positive TCP listeners
                        from flow.sdk.ssh import SshStack as _CoreS

                        if _CoreS.has_ssh_banner(task.ssh_host, int(getattr(task, "ssh_port", 22))):
                            break
                    except Exception:
                        pass
                if _t.time() - start_wait > handshake_seconds:
                    # Surface a clear failure rather than proceeding to a hang
                    timeline.fail_step(
                        "SSH did not become ready in time. Check 'flow status' and 'flow logs --source host'."
                    )
                    raise SystemExit(1)
                try:
                    adapter.update_eta()
                except Exception:
                    pass
                _t.sleep(2)

    def _connect(self, task: Task, client, command: str | None, node: int, record: bool) -> None:
        """Establish interactive session or run command on the remote host."""
        # Interactive, non-recorded sessions: exec ssh directly unless a ProxyJump is required.
        if command is None and not record:
            from flow.cli.utils.ssh_helpers import build_ssh_argv

            # Best-effort key resolution; fall back to provider flow on failure.
            ssh_argv: list[str] | None = None
            try:
                try:
                    key_path, _ = client.get_task_ssh_connection_info(task.task_id)
                except Exception:
                    key_path = None
                # Include ProxyJump when provided by provider metadata
                extra_args = None
                try:
                    pj = (getattr(task, "provider_metadata", {}) or {}).get("ssh_proxyjump")
                    if pj:
                        extra_args = ["-J", str(pj)]
                except Exception:
                    extra_args = None
                ssh_argv = build_ssh_argv(
                    user=getattr(task, "ssh_user", "ubuntu"),
                    host=getattr(task, "ssh_host", None) or "",
                    port=int(getattr(task, "ssh_port", 22) or 22),
                    key_path=str(key_path) if key_path else None,
                    extra_ssh_args=extra_args,
                    remote_command=None,
                )
                # Replace current process for a true interactive session.
                os.execvp(ssh_argv[0], ssh_argv)
            except Exception:
                # Fallback to running ssh as a subprocess with the same argv when execvp is unavailable.
                if ssh_argv:
                    subprocess.run(ssh_argv, check=False)
                    return
                # As a last resort, delegate to provider-managed shell.
                client.shell(task.task_id, node=node, progress_context=None, record=record)
                return

        # Recorded or remote-command sessions: delegate to provider (captures output when needed).
        if command:
            client.shell(
                task.task_id, command=command, node=node, progress_context=None, record=record
            )
        else:
            client.shell(task.task_id, node=node, progress_context=None, record=record)

    def _handle_connect_error(self, e: Exception, client, task: Task, timeline) -> None:
        """Render a helpful failure and a manual connection hint when possible."""
        provider_name = (
            getattr(getattr(client, "config", None), "provider", None)
            or os.environ.get("FLOW_PROVIDER")
            or "mithril"
        )
        connection_cmd = None
        with suppress(Exception):  # best-effort formatting from provider
            ProviderClass = plugin_registry.get_provider(provider_name)
            if ProviderClass and hasattr(ProviderClass, "format_connection_hint"):
                connection_cmd = ProviderClass.format_connection_hint(task)
        if connection_cmd:
            from flow.cli.utils.theme_manager import theme_manager as _tm_warn

            warn = _tm_warn.get_color("warning")
            console.print(
                f"\n[{warn}]Connection failed. You can try connecting manually with:[/{warn}]"
            )
            console.print(f"  {connection_cmd}\n")
        req_id = getattr(e, "request_id", None)
        if req_id:
            timeline.fail_step(f"{e!s}\nRequest ID: {req_id}")
        else:
            timeline.fail_step(str(e))

    def _maybe_print_next_actions(self, task: Task, ran_command: bool) -> None:
        if ran_command:
            return
        task_ref = task.name or task.task_id
        self.show_next_actions(
            [
                f"View logs: [accent]flow logs {task_ref} --follow[/accent]",
                f"Check status: [accent]flow status {task_ref}[/accent]",
                f"Run nvidia-smi: [accent]flow ssh {task_ref} -- nvidia-smi[/accent]",
                "Enter container: [accent]docker exec -it main bash -l || docker exec -it main sh -l[/accent]",
            ]
        )

    def _is_fast_mode(self) -> bool:
        """Centralized FAST mode detection supporting config and env strings."""
        try:
            from flow.application.config.runtime import settings  # local import by design

            v = (settings.ssh or {}).get("fast")
            if isinstance(v, bool):
                return v
        except Exception:
            pass
        env = os.getenv("FLOW_SSH_FAST", "").strip().lower()
        return env in {"1", "true", "yes", "on"}

    def _try_direct_exec_from_cache(
        self, task: Task, client, *, node: int, command: str | None, record: bool
    ) -> bool:
        """Try a zero-API, cache-first SSH exec for fastest UX.

        Returns True if we started ssh (process may be replaced), else False.
        """
        if command is not None or record or int(node or 0) != 0:
            return False
        # Endpoint from last status cache or task fields
        host: str | None = None
        port: int = 22
        try:
            from flow.cli.utils.task_index_cache import TaskIndexCache as _TIC

            cached = _TIC().get_cached_task(getattr(task, "task_id", ""))
            if cached:
                host = cached.get("ssh_host") or None
                try:
                    if cached.get("ssh_port") is not None:
                        port = int(cached.get("ssh_port"))
                except Exception:
                    port = 22
        except Exception:
            pass
        if not host:
            host = getattr(task, "ssh_host", None)
            try:
                if getattr(task, "ssh_port", None) is not None:
                    port = int(getattr(task, "ssh_port", 22))
            except Exception:
                port = 22
        if not host:
            return False
        # Key from cache only; if missing, defer to normal provider resolution
        try:
            from flow.core.utils.ssh_key_cache import SSHKeyCache as _KC

            key_path = _KC().get_key_path(getattr(task, "task_id", ""))
        except Exception:
            key_path = None
        if not key_path:
            return False
        from flow.cli.utils.ssh_helpers import build_ssh_argv

        ssh_argv = build_ssh_argv(
            user=getattr(task, "ssh_user", "ubuntu"),
            host=str(host),
            port=int(port or 22),
            key_path=str(key_path),
            extra_ssh_args=None,
            remote_command=None,
        )
        try:
            os.execvp(ssh_argv[0], ssh_argv)
        except Exception:
            subprocess.run(ssh_argv, check=False)
        return True

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        # Trailing command only; no -c/--command flag
        @click.option(
            "--node", type=int, default=0, help="Node index for multi-instance tasks (default: 0)"
        )
        @click.option(
            "--container",
            is_flag=True,
            hidden=True,  # hide in help to avoid false positive '-c' test
            help=(
                "Open inside the task container (docker exec) or run the given command in the container"
            ),
        )
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed help and examples")
        @click.option(
            "--json", "output_json", is_flag=True, help="Output connection parameters as JSON"
        )
        @click.option(
            "--record",
            is_flag=True,
            help="Record session to host logs (viewable with flow logs --source host)",
        )
        @click.option(
            "--fast",
            is_flag=True,
            help="Skip readiness wait; prefer cached endpoint and connect immediately",
        )
        # @demo_aware_command()
        @click.argument("remote_cmd", nargs=-1)
        @cli_error_guard(self)
        def ssh(
            task_identifier: str | None,
            node: int,
            verbose: bool,
            record: bool,
            remote_cmd: tuple[str, ...],
            output_json: bool,
            container: bool,
            fast: bool,
        ):
            """SSH to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \b
            Examples:
                flow ssh                    # Interactive task selector
                flow ssh my-training        # Connect by name
                flow ssh task-abc123        # Connect by ID
                flow ssh task -- nvidia-smi             # Run command remotely (after --)

            Use 'flow ssh --verbose' for troubleshooting and advanced examples.
            """
            if fast:
                try:
                    os.environ["FLOW_SSH_FAST"] = "1"
                except Exception:
                    pass

            if verbose:
                console.print("\n[bold]Advanced SSH Usage:[/bold]\n")
                console.print("Multi-instance tasks (0-based node index):")
                console.print("  flow ssh distributed-job --node 0    # Connect to first node")
                console.print("  flow ssh distributed-job --node 1    # Connect to second node\n")

                console.print("File transfer:")
                console.print("  scp file.py $(flow ssh task -- echo $USER@$HOSTNAME):~/")
                console.print(
                    "  rsync -av ./data/ $(flow ssh task -- echo $USER@$HOSTNAME):/data/\n"
                )

                console.print("Container mode:")
                console.print("  (Use the container flag to exec inside the main container)")
                console.print("  Examples: enter shell, or run nvidia-smi inside the container\n")

                console.print("Port forwarding:")
                console.print(
                    "  ssh -L 8888:localhost:8888 $(flow ssh task -- echo $USER@$HOSTNAME)"
                )
                console.print(
                    "  ssh -L 6006:localhost:6006 $(flow ssh task -- echo $USER@$HOSTNAME)  # TensorBoard\n"
                )

                console.print("Monitoring:")
                console.print("  flow ssh task -- watch -n1 nvidia-smi    # GPU usage")
                console.print("  flow ssh task -- htop                     # System resources")
                console.print("  flow ssh task -- tail -f output.log       # Stream logs\n")

                console.print("Troubleshooting:")
                console.print("  • No SSH info? Wait 2-5 minutes for instance provisioning")
                console.print("  • Permission denied? Run: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Connection refused? Check: flow health --task <name>")
                console.print("  • Task terminated? Check: flow status <name>\n")
                return

            # If a trailing command was provided after '--', use it
            # Normalize selection identifiers early (works after `flow status`)
            if task_identifier:
                task_identifier = self._normalize_task_identifier(task_identifier)
            command = shlex.join(remote_cmd) if remote_cmd else None

            # JSON mode requires a concrete task identifier to avoid interactive selector output
            if output_json:
                if not task_identifier:
                    raise click.UsageError("--json requires a task identifier (id or name)")
                if container:
                    raise click.UsageError("--json cannot be combined with --container")

                # Resolve and emit connection parameters
                import flow.sdk.factory as _sdk_factory
                from flow.cli.utils.json_output import print_json
                from flow.cli.utils.ssh_helpers import build_ssh_argv, ssh_command_string
                from flow.cli.utils.task_resolver import (
                    resolve_task_identifier as _resolve_identifier,
                )

                client = _sdk_factory.create_client(auto_init=True)
                # Resolve ':dev', indices, names, or IDs consistently with normal ssh flow
                task, _err = _resolve_identifier(client, task_identifier)
                if task is None:
                    # _err contains a human-readable message
                    raise click.UsageError(_err or "Task not found")
                # Try to resolve endpoint, fallback to task fields
                try:
                    host, port = client.resolve_ssh_endpoint(task.task_id, node=node)
                except Exception:
                    host = getattr(task, "ssh_host", None)
                    port = int(getattr(task, "ssh_port", 22) or 22)
                user = getattr(task, "ssh_user", "ubuntu")
                key_path = None
                try:
                    key_path, _err = client.get_task_ssh_connection_info(task.task_id)
                except Exception:
                    key_path = None
                ssh_argv = build_ssh_argv(
                    user=user,
                    host=host,
                    port=port,
                    key_path=str(key_path) if key_path else None,
                    extra_ssh_args=None,
                    remote_command=None,
                )
                cmd = ssh_command_string(ssh_argv)
                print_json(
                    {
                        "user": user,
                        "host": host,
                        "port": port,
                        "key_path": str(key_path) if key_path else None,
                        "ssh_command": cmd,
                        "task_id": task.task_id,
                        "task_name": getattr(task, "name", None),
                        "node": node,
                    }
                )
                return

            # Transform command for container mode before execution
            if container:
                command = self._wrap_container_cmd(command, interactive=not bool(command))

            self._execute(task_identifier, command, node, record, fast=fast)

        return ssh

    def _execute(
        self,
        task_identifier: str | None,
        command: str | None,
        node: int = 0,
        record: bool = False,
        *,
        fast: bool = False,
    ) -> None:
        """Execute SSH connection or command."""
        # For non-interactive commands, use standard flow
        if command:
            self.execute_with_selection(
                task_identifier, command=command, node=node, record=record, fast=fast
            )
            return

        # Delegate to selection without pre-animations; the timeline inside execute_on_task owns the UX
        self.execute_with_selection(
            task_identifier,
            command=command,
            node=node,
            record=record,
            fast=fast,
        )

    # ----- CLI-facing utilities -----
    def _normalize_task_identifier(self, raw: str) -> str:
        """Normalize selection grammar to a single task id or raise UsageError."""
        from flow.cli.utils.selection_helpers import parse_selection_to_task_ids

        ids, err = parse_selection_to_task_ids(raw)
        if err:
            raise click.UsageError(err)
        if ids is not None:
            if len(ids) != 1:
                raise click.UsageError("Selection must resolve to exactly one task for ssh")
            return ids[0]
        return raw

    # Deprecated -c/--command flag removed; trailing command is the supported path

    def _wrap_container_cmd(self, user_cmd: str | None, interactive: bool) -> str | None:
        """Wrap a user command to run inside the main container, or pick an interactive shell.

        Always run via POSIX shell inside the container; prefer bash if present.
        """
        if user_cmd:
            return f"docker exec main sh -lc {shlex.quote(user_cmd)}"
        return "docker exec -it main bash -l || docker exec -it main sh -l" if interactive else None


# Export command instance
command = SSHCommand()
