"""Upload code command for transferring local code to running tasks.

This command provides manual code upload functionality using SCP/rsync,
useful for updating code on long-running instances without restarting.
"""

from pathlib import Path

import click

from flow.cli.commands.base import BaseCommand, console
from flow.cli.utils.step_progress import StepTimeline, UploadProgressReporter
from flow.cli.utils.task_selector_mixin import TaskOperationCommand
from flow.errors import FlowError


class UploadCodeCommand(BaseCommand, TaskOperationCommand):
    """Upload code to a running task.

    Transfers local code to a running GPU instance using efficient
    rsync-based transfer with progress reporting.
    """

    @property
    def name(self) -> str:
        return "upload-code"

    @property
    def help(self) -> str:
        return "Upload local code to running tasks - incremental sync via rsync"

    @property
    def manages_own_progress(self) -> bool:
        """Upload-code manages its own progress display for smooth transitions."""
        return True

    # TaskSelectorMixin implementation
    def get_task_filter(self):
        """Show running tasks (SSH may still be provisioning)."""
        from flow.cli.utils.task_selector_mixin import TaskFilter

        return TaskFilter.running_only

    def get_selection_title(self) -> str:
        return "Select a task to upload code to"

    def get_no_tasks_message(self) -> str:
        return "No running tasks found. Start a task first with 'flow run'"

    def execute_on_task(self, task, client, **kwargs) -> None:
        """Execute code upload on the selected task."""
        source_dir = kwargs.get("source")
        timeout = kwargs.get("timeout", 600)
        dest = kwargs.get("dest")
        json_mode = bool(kwargs.get("output_json", False))
        git_incremental = bool(kwargs.get("incremental", False))

        # Validate source directory
        if source_dir:
            source_path = Path(source_dir).resolve()
            if not source_path.exists():
                raise FlowError(f"Source directory does not exist: {source_path}")
            if not source_path.is_dir():
                raise FlowError(f"Source must be a directory: {source_path}")
        else:
            source_path = Path.cwd()

        # If no explicit source and task has a code_root, use it for default upload
        try:
            if kwargs.get("source") is None and getattr(
                getattr(task, "config", None), "code_root", None
            ):
                source_path = Path(task.config.code_root).resolve()
                console.print(f"[dim]Using task code_root: {source_path}[/dim]")
        except Exception:
            pass

        # Resolve destination directory: prefer configured default, else safe per-project under $HOME.
        from flow.application.config.runtime import settings as _settings

        try:
            project_name = source_path.name if source_path and source_path.name else "project"
        except Exception:
            project_name = "project"
        default_dest_tpl = (_settings.upload or {}).get("default_dest", "~/{project}")
        try:
            configured_default = str(default_dest_tpl).replace("{project}", project_name)
        except Exception:
            configured_default = f"~/{project_name}"
        target_dir = dest or configured_default

        task_ref = getattr(task, "name", None) or getattr(task, "task_id", "")
        if not json_mode:
            console.print(f"[dim]Preparing upload to {task_ref}[/dim]\n")
        # source_path already finalized above (may come from task.config.code_root)

        # Unified transfer timeline with Ctrl+C hint
        timeline = StepTimeline(console, title="flow upload-code", title_animation="auto")
        timeline.start()
        # Provide a gentle moving bar by default (mirrors flow dev) so users see motion
        # immediately on small uploads before real progress events arrive.
        # Start with a gentle generic estimate so users see motion during
        # rsync scanning. Real transfer progress will replace this smoothly.
        upload_idx = timeline.add_step(
            "Uploading code",
            show_bar=True,
        )
        timeline.start_step(upload_idx)
        result = None
        try:
            # Use provider's upload with timeline-based reporter and no provider console prints
            reporter = UploadProgressReporter(timeline, upload_idx)
            # Hint about safe interruption
            try:
                from rich.text import Text

                from flow.cli.utils.theme_manager import theme_manager

                accent = theme_manager.get_color("accent")
                hint = Text()
                hint.append("  Press ")
                hint.append("Ctrl+C", style=accent)
                hint.append(" to cancel upload. Instance remains running; re-run ")
                hint.append("flow upload-code", style=accent)
                hint.append(" later.")
                timeline.set_active_hint_text(hint)
            except Exception:
                pass
            result = client.upload_code_to_task(
                task_id=task.task_id,
                source_dir=source_path,
                timeout=timeout,
                console=None,
                progress_reporter=reporter,
                target_dir=target_dir,
                git_incremental=git_incremental,
                prepare_absolute=kwargs.get("prepare_absolute", False) or None,
            )
        except KeyboardInterrupt:
            if json_mode:
                from flow.cli.utils.json_output import error_json, print_json

                print_json(error_json("Upload interrupted by user"))
            else:
                console.print(
                    "\n[dim]Upload interrupted by user. Instance remains running. Re-run: flow upload-code[/dim]"
                )
        except Exception as e:
            # Check for dependency errors - providers should raise DependencyNotFoundError
            # but we handle string matching for backward compatibility
            if "rsync not found" in str(e):
                if json_mode:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(
                        error_json(
                            "rsync is required for code upload", hint="Install rsync (brew/apt/yum)"
                        )
                    )
                else:
                    console.print("[error]Error:[/error] rsync is required for code upload\n")
                    console.print("Install rsync:")
                    console.print("  • macOS: [accent]brew install rsync[/accent]")
                    console.print("  • Ubuntu/Debian: [accent]sudo apt-get install rsync[/accent]")
                    console.print("  • RHEL/CentOS: [accent]sudo yum install rsync[/accent]")
            else:
                if json_mode:
                    from flow.cli.utils.json_output import error_json, print_json

                    print_json(error_json(str(e)))
                else:
                    raise
        finally:
            timeline.finish()

        # Print a crisp success summary after the timeline is closed
        if result is not None:
            try:
                bt = getattr(result, "bytes_transferred", 0) or 0
                ft = getattr(result, "files_transferred", 0) or 0
                rate = getattr(result, "transfer_rate", None)
                final_target = getattr(result, "final_target", None) or target_dir
                size_mb = bt / (1024 * 1024)
                if json_mode:
                    from flow.cli.utils.json_output import print_json

                    print_json(
                        {
                            "status": "ok",
                            "task_id": getattr(task, "task_id", None),
                            "task_name": getattr(task, "name", None),
                            "source": str(source_path),
                            "dest": final_target,
                            "files_transferred": ft,
                            "bytes_transferred": bt,
                            "transfer_rate": rate,
                        }
                    )
                else:
                    if ft == 0 and bt == 0:
                        console.print(f"[dim]No changes to sync → {task_ref}:{final_target}[/dim]")
                    else:
                        msg = (
                            f"[success]✓[/success] Upload complete: {ft} files, {size_mb:.1f} MB"
                            f" → {task_ref}:{final_target}"
                        )
                        if isinstance(rate, str) and rate:
                            msg += f" @ {rate}"
                        console.print(msg)
            except Exception:
                pass

            # Next steps
            if not json_mode:
                task_ref = task.name or task.task_id
                self.show_next_actions(
                    [
                        f"SSH into instance: [accent]flow ssh {task_ref}[/accent]",
                        f"View logs: [accent]flow logs {task_ref} -f[/accent]",
                        "Run your updated code in the SSH session",
                    ]
                )

    def get_command(self) -> click.Command:
        # Import completion function
        # from flow.cli.utils.mode import demo_aware_command
        from flow.cli.ui.runtime.shell_completion import complete_task_ids

        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False, shell_complete=complete_task_ids)
        @click.option(
            "--source",
            "-s",
            type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
            help="Source directory to upload (default: current directory)",
        )
        @click.option(
            "--timeout",
            "-t",
            type=int,
            default=600,
            help="Upload timeout in seconds (default: 600)",
        )
        @click.option(
            "--dest",
            type=str,
            default=None,
            help=(
                "Destination directory on the instance (default from config: ~/{project}; use --dest /workspace on prepared instances)."
            ),
        )
        @click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Show detailed upload patterns and troubleshooting",
        )
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option(
            "--incremental/--full-scan",
            default=False,
            help=(
                "Use Git to detect changed/untracked files and only upload those (default: full scan). "
                "Requires a Git repository."
            ),
        )
        @click.option(
            "--prepare-absolute",
            is_flag=True,
            default=False,
            help=(
                "Use sudo -n to prepare absolute destinations (mkdir/chown) when unwritable. "
                "Defaults to config/env when omitted."
            ),
        )
        # @demo_aware_command()
        def upload_code(
            task_identifier: str | None,
            source: Path | None,
            timeout: int,
            verbose: bool,
            dest: str | None,
            output_json: bool,
            incremental: bool,
            prepare_absolute: bool = False,
        ):
            """Upload code to a running task.

            TASK_IDENTIFIER: Task ID or name (optional - interactive selector if omitted)

            \\b
            Examples:
                flow upload-code                 # Interactive task selector
                flow upload-code my-training     # Upload to specific task
                flow upload-code -s ../lib       # Upload different directory
                flow upload-code -t 1200         # Longer timeout (20 min)

            Default destination is ~/<project>. This is user-writable and avoids permission issues.
            Use --dest to override (e.g., --dest /workspace on instances where it's writable).

            Use 'flow upload-code --verbose' for advanced patterns and .flowignore guide.
            """
            if verbose and not output_json:
                from flow.cli.utils.icons import flow_icon as _flow_icon

                console.print(f"\n[bold]{_flow_icon()} Code Upload Guide:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow upload-code                  # Upload current directory")
                console.print("  flow upload-code my-task          # Upload to specific task")
                console.print("  flow upload-code -s ~/project     # Upload different source\n")

                console.print("Upload behavior:")
                console.print("  • Destination: ~/<project> by default (user-writable)")
                console.print("    - Override with: --dest /workspace (or any absolute path)")
                console.print("  • Method: rsync with compression")
                console.print("  • Incremental: Only changed files uploaded")
                console.print("  • Progress: Real-time transfer status\n")

                console.print(".flowignore patterns:")
                console.print("  # Common patterns to exclude:")
                console.print("  .git/")
                console.print("  __pycache__/")
                console.print("  *.pyc")
                console.print("  .env")
                console.print("  venv/")
                console.print("  node_modules/")
                console.print("  *.log")
                console.print("  .DS_Store\n")

                console.print("Large project optimization:")
                console.print("  # Create minimal .flowignore")
                console.print("  echo 'data/' >> .flowignore       # Exclude large datasets")
                console.print("  echo 'models/' >> .flowignore     # Exclude model weights")
                console.print("  echo '.git/' >> .flowignore       # Exclude git history\n")

                console.print("Common workflows:")
                console.print("  # Hot reload during development")
                console.print("  flow upload-code && flow ssh task -- python train.py")
                console.print("  ")
                console.print("  # Upload and monitor")
                console.print("  flow upload-code && flow logs task -f")
                console.print("  ")
                console.print("  # Sync specific module")
                console.print("  flow upload-code -s ./src/models\n")

                console.print("Troubleshooting:")
                console.print("  • Timeout errors → Increase with -t 1800 (30 min)")
                console.print("  • rsync not found → Install: brew/apt/yum install rsync")
                console.print("  • Permission denied → Check task is running: flow status")
                console.print("  • Upload too slow → Add more patterns to .flowignore\n")

                console.print("Next steps after upload:")
                console.print("  • Connect: flow ssh [task.name]<task-name>[/task.name]")
                console.print("  • Run code: python your_script.py")
                console.print("  • Monitor: flow logs [task.name]<task-name>[/task.name] -f\n")
                return

            self._execute(
                task_identifier,
                source=source,
                timeout=timeout,
                dest=dest,
                output_json=output_json,
                incremental=incremental,
                prepare_absolute=prepare_absolute,
            )

        return upload_code

    def _execute(
        self,
        task_identifier: str | None,
        source: Path | None,
        timeout: int,
        dest: str | None,
        *,
        output_json: bool = False,
        incremental: bool = False,
        prepare_absolute: bool = False,
    ) -> None:
        """Execute the upload-code command."""
        self.execute_with_selection(
            task_identifier,
            source=source,
            timeout=timeout,
            dest=dest,
            output_json=output_json,
            incremental=incremental,
            prepare_absolute=prepare_absolute,
        )


# Export command instance
command = UploadCodeCommand()
