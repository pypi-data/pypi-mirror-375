"""flow status command.

Lists and monitors GPU compute tasks with filtering (state, time window, project),
snapshot and live views, and JSON output for automation. See `flow status --help`
for CLI usage and examples.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING

import click

import flow.sdk.factory as sdk_factory
from flow.cli.commands.base import BaseCommand, console
from flow.cli.constants import DEFAULT_STATUS_LIMIT
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress

# Avoid importing heavy UI modules at import time; import lazily inside the command
from flow.cli.utils.error_handling import cli_error_guard
from flow.errors import AuthenticationError, FlowError

# Back-compat: expose Flow for tests that patch flow.cli.commands.status.Flow
from flow.sdk.client import Flow as Flow


class StatusCommand(BaseCommand):
    """List tasks with optional filtering."""

    def __init__(self):
        """Initialize command with task presenter.

        Avoid creating Flow() at import time to prevent environment-dependent
        side effects during module import (e.g., smoke import or docs build).
        The presenter will lazily create a Flow client on first use.
        """
        super().__init__()
        if TYPE_CHECKING:  # pragma: no cover - only for typing
            from flow.cli.ui.facade.views import TaskPresenter as _TaskPresenter
        self.task_presenter: _TaskPresenter | None = None

    @property
    def name(self) -> str:
        return "status"

    @property
    def help(self) -> str:
        return "List and monitor GPU compute tasks - filter by status, name, or time"

    def get_command(self) -> click.Command:
        from flow.cli.ui.runtime.shell_completion import complete_task_ids as _complete_task_ids

        def _dbg(msg: str) -> None:
            if os.environ.get("FLOW_STATUS_DEBUG"):
                logging.getLogger("flow.status.cli").debug(msg)

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=_complete_task_ids)
        @click.option(
            "--all",
            "show_all",
            is_flag=True,
            help="Show all tasks (default: active tasks only)",
        )
        @click.option(
            "--active",
            is_flag=True,
            help="Show only active tasks (running, pending) [default]",
            hidden=True,  # Back-compat flag; default behavior is active-only
        )
        # Demo toggle disabled for initial release
        # @click.option("--demo/--no-demo", default=None, help="Override demo mode for this command (mock provider, no real provisioning)")
        @click.option(
            "--state",
            "-s",
            type=click.Choice(
                ["pending", "running", "paused", "preempting", "completed", "failed", "cancelled"]
            ),
            help="Filter by state",
        )
        @click.option(
            "--limit",
            default=DEFAULT_STATUS_LIMIT,
            help="Maximum number of tasks to show",
        )
        @click.option(
            "--force-refresh",
            is_flag=True,
            help="Bypass local caches and fetch fresh task data from provider",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--since",
            type=str,
            help="Only tasks created since time (e.g., '2h', '2025-08-07T10:00:00Z')",
        )
        @click.option(
            "--until", type=str, help="Only tasks created until time (same formats as --since)"
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed status information and filtering examples",
        )
        @click.option("--watch", "-w", is_flag=True, help="Live update the status display")
        @click.option("--compact", is_flag=True, help="Compact allocation view")
        @click.option(
            "--refresh-rate",
            default=3.0,
            type=float,
            help="Refresh rate in seconds for watch mode (default: 3)",
        )
        @click.option(
            "--project",
            type=str,
            required=False,
            help="Filter to a specific project/workspace (provider dependent)",
        )
        @click.option(
            "--no-origin-group", is_flag=True, help="Disable Flow/Other grouping in main view"
        )
        @click.option(
            "--show-reservations",
            is_flag=True,
            help="Show an additional Reservations panel (upcoming and active)",
            hidden=True,
        )
        @click.option(
            "--interactive/--no-interactive",
            default=None,
            help="When ambiguous identifier matches multiple tasks: open selector (default: auto if TTY)",
        )
        # @demo_aware_command(flag_param="demo")
        @cli_error_guard(self)
        def status(
            task_identifier: str | None,
            show_all: bool,
            active: bool,
            state: str | None,
            limit: int,
            output_json: bool,
            since: str | None,
            until: str | None,
            verbose: bool,
            watch: bool,
            compact: bool,
            refresh_rate: float,
            project: str | None,
            no_origin_group: bool,
            show_reservations: bool,
            # demo: bool | None,
            force_refresh: bool,
            interactive: bool | None,
        ):
            """List tasks or show details for a specific task.

            \b
            Examples:
                flow status                  # Active tasks (default)
                flow status my-training      # Find task by name
                flow status --state running  # Only running tasks
                flow status --active         # Only active tasks (running/pending)
                flow status --watch          # Live updating display
                flow status -w --refresh-rate 1  # Update every second

            Use 'flow status --verbose' for advanced filtering and monitoring patterns.
            """
            # Ensure --project affects any Flow() created below by setting env early
            from flow.cli.services.status_setup import apply_project_env

            apply_project_env(project)
            _dbg(
                f"status: args project={project} show_all={show_all} state={state} limit={limit} "
                f"since={since} until={until} json={output_json} watch={watch} compact={compact}"
            )
            _dbg(
                "status: env FLOW_PROVIDER="
                + str(os.environ.get("FLOW_PROVIDER"))
                + " MITHRIL_PROJECT="
                + str(os.environ.get("MITHRIL_PROJECT"))
                + " MITHRIL_PROJECT_ID="
                + str(os.environ.get("MITHRIL_PROJECT_ID"))
            )

            # Compute effective show_all using a focused default: active-only
            # - --all overrides to include completed/cancelled
            # - --state applies specific filtering
            # - default (no flags) shows only active (running/pending)
            effective_show_all = bool(show_all)

            # Emit a gentle deprecation notice if --active is used
            if active:
                try:
                    console.print(
                        "[dim]Note: --active is now the default and will be removed in a future release. Use --all to include completed.[/dim]"
                    )
                except Exception:
                    pass

            if force_refresh:
                # Clear prefetch caches before proceeding
                from flow.cli.services.status_setup import apply_force_refresh

                _dbg("status: force-refresh requested → clearing caches")
                apply_force_refresh()

            # Create a single Flow client for this command execution and reuse it
            # across all downstream calls to avoid repeated provider initialization.
            client = None

            # Lazily construct presenter now that imports are resolved
            if self.task_presenter is None:
                try:
                    from flow.cli.ui.facade.views import TaskPresenter as _TaskPresenter

                    self.task_presenter = _TaskPresenter(console)
                except Exception:
                    # Leave presenter as None; we will fall back to a simple renderer below
                    self.task_presenter = None

            if verbose and not task_identifier:
                try:
                    from flow.cli.ui.facade.views import render_verbose_help as _render_verbose_help

                    _render_verbose_help(console)
                    return
                except Exception:
                    console.print(
                        "[dim]Verbose help unavailable (UI components missing). Proceeding with basic status view.[/dim]"
                    )

            # Demo mode already applied by decorator

            # Specific task: delegate to actions with interactive fallback on ambiguity
            if (not output_json) and task_identifier and (not watch):
                _dbg("status: path=single-task (no watch/json)")
                from flow.cli.services.status_actions import present_single_or_interactive

                if client is None:
                    client = sdk_factory.create_client(auto_init=True)
                handled = present_single_or_interactive(
                    console,
                    task_identifier,
                    state=state,
                    interactive=interactive,
                    flow_client=client,
                )
                if handled:
                    return

            # Default snapshot view: show AEP as early as possible, including client init
            if (not output_json) and (not task_identifier) and (not watch):
                _dbg("status: path=snapshot (no id/json/watch)")
                # If not attached to a TTY (e.g., tests/CI), prefer a simple, deterministic list.
                try:
                    if (not getattr(console, "is_terminal", False)) or os.environ.get(
                        "PYTEST_CURRENT_TEST"
                    ):
                        _dbg("status: non-TTY/pytest detected → using simple list renderer")
                        if client is None:
                            try:
                                client = sdk_factory.create_client(auto_init=True)
                            except AuthenticationError:
                                # Back-compat for tests that patch Flow in this module
                                try:
                                    client = Flow(auto_init=False)  # type: ignore
                                except Exception:
                                    client = None
                        self._render_simple_list(
                            show_all=effective_show_all,
                            state=state,
                            limit=limit,
                            since=since,
                            until=until,
                            flow_client=client,
                        )
                        return
                except Exception:
                    # If detection fails, proceed with rich path below
                    pass

                # Build presenter and options; if imports fail, fallback to simple list.
                try:
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusDisplayOptions as _SDO,
                    )
                    from flow.cli.ui.presentation.status_presenter import (
                        StatusPresenter as _Presenter,
                    )
                except Exception:
                    _dbg("status: snapshot UI imports unavailable → fallback to simple list")
                    # Ensure client exists for fallback rendering
                    if client is None:
                        try:
                            client = sdk_factory.create_client(auto_init=True)
                        except AuthenticationError:
                            try:
                                client = Flow(auto_init=False)  # type: ignore
                            except Exception:
                                client = None
                    self._render_simple_list(
                        show_all=effective_show_all,
                        state=state,
                        limit=limit,
                        since=since,
                        until=until,
                        flow_client=client,
                    )
                    return

                # Start AEP before any potentially slow steps (client/provider init)
                me_ctx = None
                owner_map = None
                with AnimatedEllipsisProgress(
                    console, "Preparing status view", start_immediately=True
                ) as progress:
                    # Lazily create the Flow client inside AEP to avoid pre-spinner stalls
                    if client is None:
                        _dbg("status: creating client inside AEP")
                        try:
                            client = sdk_factory.create_client(auto_init=True)
                        except AuthenticationError:
                            # Back-compat for tests that patch Flow in this module
                            try:
                                client = Flow(auto_init=False)  # type: ignore
                            except Exception:
                                client = None

                    # Default snapshot behavior: show active tasks; if none, show recent.
                    # Use --all for full historical lists.
                    options = _SDO(
                        show_all=effective_show_all,
                        limit=limit,
                        group_by_origin=(not no_origin_group),
                        status_filter=(state or None),
                    )

                    presenter = _Presenter(console, flow_client=client)

                    # Switch message once ready to fetch
                    try:
                        progress.update_message("Fetching tasks")
                    except Exception:
                        pass
                    # Use the presenter's fetcher to avoid printing under AEP
                    if client is None:
                        tasks = []
                        me_ctx = None
                        owner_map = None
                    else:
                        tasks = presenter.fetcher.fetch_for_display(
                            show_all=options.show_all,
                            status_filter=options.status_filter,
                            limit=options.limit,
                        )
                        # Resolve identity context while AEP is still active to avoid a perceived hang
                        try:
                            progress.update_message("Resolving owners")
                        except Exception:
                            pass
                        try:
                            from flow.cli.ui.runtime.owner_resolver import (
                                OwnerResolver as _OwnerResolver,
                            )

                            _resolver = _OwnerResolver(client)
                            me_ctx = _resolver.get_me()
                            owner_map = _resolver.get_teammates_map()
                        except Exception:
                            me_ctx = None
                            owner_map = None

                # Now render outside the AEP to avoid Live/print interleaving.
                # The presenter handles recommendations (Next Steps) internally.
                try:
                    if client is None:
                        # Minimal deterministic output if client creation failed
                        self._render_simple_list(
                            show_all=effective_show_all,
                            state=state,
                            limit=limit,
                            since=since,
                            until=until,
                            flow_client=None,
                        )
                    else:
                        # Use fast path and pre-resolved owner context to keep UX responsive
                        presenter.present(
                            options,
                            tasks=tasks,
                            me=me_ctx,
                            owner_map=owner_map,
                            fast=True,
                        )
                except Exception:
                    _dbg("status: snapshot presenter failed; rendering simple list fallback")
                    self._render_simple_list(
                        show_all=effective_show_all,
                        state=state,
                        limit=limit,
                        since=since,
                        until=until,
                        flow_client=client,
                    )
                return

            _dbg("status: path=execute (json/watch or simple modes)")
            self._execute(
                task_identifier,
                effective_show_all,
                state,
                limit,
                output_json,
                since,
                until,
                watch,
                compact,
                refresh_rate,
                no_origin_group,
                flow_client=client,
            )

        return status

    def _derive_priority(self, task) -> str | None:
        """Best-effort derivation of priority tier for a task.

        Prefers explicit config priority when attached; otherwise infers from
        provider metadata (e.g., limit price vs per‑GPU pricing) when feasible.
        Falls back to 'med' when nothing is available, matching SDK defaults.
        """
        try:
            # 1) From attached config if present
            cfg = getattr(task, "config", None)
            prio = getattr(cfg, "priority", None) if cfg is not None else None
            if prio:
                return str(prio)

            # 2) Infer from provider metadata and instance_type (optional)
            meta = getattr(task, "provider_metadata", {}) or {}
            limit_price_str = meta.get("limit_price")
            instance_type = getattr(task, "instance_type", None)
            if isinstance(limit_price_str, str) and instance_type:
                # Normalize: "$12.34" -> 12.34
                try:
                    from flow.resources import get_gpu_pricing as get_pricing_data

                    def _parse_price(s: str) -> float:
                        try:
                            return float(s.strip("$"))
                        except Exception:
                            return 0.0

                    def _extract_gpu_info(inst: str) -> tuple[str, int]:
                        try:
                            s = (inst or "").lower()
                            if "x" in s:
                                count, rest = s.split("x", 1)
                                return rest, max(1, int(count))
                            return s, 1
                        except Exception:
                            return s, 1

                    price_val = _parse_price(limit_price_str)
                    gpu_type, gpu_count = _extract_gpu_info(instance_type)
                    pricing = get_pricing_data().get("gpu_pricing", {})
                    table = pricing.get(gpu_type, pricing.get("default", {}))
                    med_per_gpu = table.get("med", 4.0)
                    med_total = med_per_gpu * max(1, gpu_count)
                    if price_val <= med_total * 0.75:
                        return "low"
                    if price_val >= med_total * 1.5:
                        return "high"
                    return "med"
                except Exception:
                    pass

            # 3) Default
            return "med"
        except Exception:
            return "med"

    def _parse_timespec(self, value: str | None) -> datetime | None:
        from flow.cli.utils.time_spec import parse_timespec

        return parse_timespec(value)

    def _to_status_enum(self, value: str | None):
        """Convert a string status to the SDK's TaskStatus enum, or None.

        Returns None on invalid values to keep filtering permissive at the CLI layer.
        """
        try:
            if not value:
                return None
            from flow.sdk.models import TaskStatus as _TS

            return _TS(value)
        except Exception:
            return None

    def _execute(
        self,
        task_identifier: str | None,
        show_all: bool,
        status: str | None,
        limit: int,
        output_json: bool,
        since: str | None,
        until: str | None,
        watch: bool = False,
        compact: bool = False,
        refresh_rate: float = 3.0,
        no_origin_group: bool = False,
        flow_client=None,
    ) -> None:
        """Execute the status command."""
        # Cannot use watch mode with JSON output or specific task identifier
        if watch and (output_json or task_identifier):
            raise click.UsageError(
                "--watch cannot be combined with --json or a specific TASK_ID_OR_NAME"
            )

        # JSON output mode - no animation
        if output_json:
            from flow.cli.services.status_queries import StatusQuery, parse_timespec
            from flow.cli.utils.json_output import error_json, print_json, task_to_json
            from flow.cli.utils.task_fetcher import TaskFetcher

            client = flow_client or sdk_factory.create_client(auto_init=True)
            if task_identifier:
                try:
                    task = client.get_task(task_identifier)
                    print_json(task_to_json(task))
                    return
                except FlowError as e:
                    print_json(error_json(str(e)))
                    return
            else:
                query = StatusQuery(
                    task_identifier=None,
                    show_all=show_all,
                    state=status,
                    limit=limit,
                    since=parse_timespec(since),
                    until=parse_timespec(until),
                )
                # Delegate fetching semantics (active-first, then recent) to TaskFetcher
                fetcher = TaskFetcher(client)
                tasks = fetcher.fetch_for_display(
                    show_all=query.show_all, status_filter=query.state, limit=query.limit
                )
                if query.since or query.until:
                    from flow.cli.services.status_queries import filter_by_time

                    tasks = filter_by_time(tasks, query.since, query.until)
                print_json([task_to_json(t) for t in tasks])
                return

        # Check if we're in watch mode
        if watch:
            # If compact is requested, use alloc-like live view; else keep existing live table
            try:
                if compact:
                    from flow.cli.ui.facade.views import run_live_compact as _run_live_compact

                    _run_live_compact(
                        console,
                        show_all=show_all,
                        status_filter=status,
                        limit=limit,
                        refresh_rate=refresh_rate,
                        flow_client=flow_client,
                    )
                else:
                    from flow.cli.ui.facade.views import run_live_table as _run_live_table

                    _run_live_table(
                        console,
                        show_all=show_all,
                        status_filter=status,
                        limit=limit,
                        refresh_rate=refresh_rate,
                        flow_client=flow_client,
                    )
            except Exception:
                console.print(
                    "[error]Live view unavailable (UI components missing). Showing static list instead.[/error]"
                )
                self._render_simple_list(
                    show_all=show_all,
                    state=status,
                    limit=limit,
                    since=since,
                    until=until,
                    flow_client=flow_client,
                )
            return

        # Start animation immediately for instant feedback
        progress = AnimatedEllipsisProgress(
            console,
            "Fetching tasks" if not task_identifier else "Looking up task",
            start_immediately=True,
        )

        try:
            # Handle specific task request
            if task_identifier:
                with progress:
                    from flow.cli.services.status_presenter_flow import present_single_task

                    if not present_single_task(
                        console, self.task_presenter, task_identifier, flow_client=flow_client
                    ):
                        return
            else:
                # Present task list with optional time filtering via helper
                with progress:
                    try:
                        from flow.cli.ui.facade.views import present_snapshot as _present_snapshot

                        _present_snapshot(
                            console,
                            show_all=show_all,
                            state=status,
                            limit=limit,
                            group_by_origin=(not no_origin_group),
                            flow_client=(flow_client or sdk_factory.create_client(auto_init=True)),
                        )
                        summary = None
                    except Exception:
                        self._render_simple_list(
                            show_all=show_all,
                            state=status,
                            limit=limit,
                            since=None,
                            until=None,
                            flow_client=flow_client,
                        )
                        summary = None

                # Recommendations (Next Steps) are rendered by the presenter invoked via present_snapshot.

        except AuthenticationError:
            self.handle_auth_error()
        except click.exceptions.Exit:
            # Ensure we don't print error messages twice
            raise
        except Exception as e:
            self.handle_error(e)

    # Live mode helpers now delegated via presentation.status_view

    def _render_simple_list(
        self,
        *,
        show_all: bool,
        state: str | None,
        limit: int,
        since: str | None,
        until: str | None,
        flow_client=None,
    ) -> None:
        """Render a minimal task list without rich UI dependencies."""
        try:
            from flow.cli.services.status_queries import StatusQuery, filter_by_time, parse_timespec
            from flow.cli.utils.task_fetcher import TaskFetcher
        except Exception:
            console.print(
                "[error]Unable to load status helpers. Please reinstall the package or run with --json.[/error]"
            )
            return

        # Best-effort client creation for non-interactive or test environments
        if flow_client is not None:
            client = flow_client
        else:
            try:
                client = sdk_factory.create_client(auto_init=True)
            except AuthenticationError:
                # Back-compat for tests that patch Flow symbol in this module
                try:
                    client = Flow(auto_init=False)  # type: ignore
                except Exception:
                    client = None

        # Delegate to TaskFetcher for consistent semantics
        status_enum = self._to_status_enum(state)
        tasks = []
        try:
            if client is not None:
                fetcher = TaskFetcher(client)
                tasks = fetcher.fetch_for_display(
                    show_all=bool(show_all),
                    status_filter=(status_enum.value if status_enum else None),
                    limit=limit,
                )
        except AuthenticationError:
            tasks = []
        qs = StatusQuery(
            task_identifier=None,
            show_all=bool(show_all),
            state=state,
            limit=limit,
            since=parse_timespec(since),
            until=parse_timespec(until),
        )
        if qs.since or qs.until:
            tasks = filter_by_time(tasks, qs.since, qs.until)

        if not tasks:
            try:
                from flow.cli.ui.presentation.nomenclature import get_entity_labels as _labels

                noun = _labels().empty_plural
            except Exception:
                noun = "tasks"
            console.print(f"No {noun} found. Run 'flow run' to submit a job.")
            return

        # In minimal mode, avoid Rich markup/highlighting so tests and piping
        # see plain, searchable text without ANSI escapes.
        console.print("Tasks (minimal):", markup=False, highlight=False)
        for t in tasks:
            tid = getattr(t, "task_id", "")
            name = getattr(t, "name", "")
            status_val = getattr(getattr(t, "status", None), "value", "")
            itype = getattr(t, "instance_type", "")
            # Uppercase GPU type for display consistency with rich table
            itype_disp = str(itype).upper() if isinstance(itype, str) else str(itype)
            created = getattr(t, "created_at", None)
            created_str = getattr(created, "isoformat", lambda: str(created))()
            console.print(
                f"- {name} status={status_val} id={tid} gpu={itype_disp} created={created_str}",
                markup=False,
                highlight=False,
            )


# Export command instance
command = StatusCommand()
