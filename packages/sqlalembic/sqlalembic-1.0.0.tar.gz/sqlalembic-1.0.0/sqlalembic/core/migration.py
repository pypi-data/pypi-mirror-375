import subprocess
import sys
from typing import Dict, Any, Tuple
from pathlib import Path


class MigrationCommands:
    """
    Comprehensive command-line interface for managing database migrations using Alembic.
    Provides all essential migration operations with advanced features.
    """
    
    def __init__(self, dependencies: Dict[str, Any]):
        """
        Initializes MigrationCommands with core dependencies.
        """
        self.config = dependencies["config"]
        self.logger = dependencies["logger"]
        self.dispatcher = dependencies["dispatcher"]
        self.logger.info("MigrationCommands initialized with comprehensive features.")

    def _run_alembic(self, command: str, *args: str, capture_output: bool = False) -> Tuple[bool, str, str]:
        """
        Runs an alembic command as a subprocess from the project root.
        Emits 'alembic_command_started', 'alembic_command_completed'

        Args:
            command: The Alembic command (e.g., 'revision', 'upgrade', 'downgrade').
            *args: Additional arguments for the Alembic command.
            capture_output: If True, returns output instead of printing it.

        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        alembic_executable = 'alembic'
        full_command = [alembic_executable, command] + list(args)
        command_str = ' '.join(full_command)
        self.logger.info(f"Running Alembic command: {command_str}")
        self.dispatcher.send("alembic_command_started", sender=self, command=command, args=args, full_command=full_command)
        self.logger.debug(f"Signal 'alembic_command_started' sent for command '{command}'.")

        process = None
        stdout, stderr = "", ""
        returncode = None
        success = False
        error_type = None
        exception = None

        try:
            process = subprocess.Popen(
                full_command,
                cwd=self.config.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout, stderr = process.communicate()
            returncode = process.returncode

            if not capture_output:
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr, file=sys.stderr)

            if returncode != 0:
                self.logger.error(f"Alembic command '{command}' failed with exit code {returncode}")
                success = False
                error_type = "non_zero_exit_code"
            else:
                self.logger.info(f"Alembic command '{command}' completed successfully.")
                success = True

        except FileNotFoundError:
            error_msg = "Alembic executable not found. Make sure Alembic is installed in your virtual environment."
            self.logger.error(error_msg)
            if not capture_output:
                print(f"\nError: {error_msg} (pip install alembic)", file=sys.stderr)
            success = False
            error_type = "alembic_not_found"
            stderr = error_msg

        except Exception as e:
            self.logger.exception(f"An unexpected error occurred while running Alembic command '{command}': {e}")
            success = False
            error_type = "exception"
            exception = e
            stderr = str(e)

        if success:
            self.dispatcher.send("alembic_command_completed", sender=self, command=command, args=args, 
                                returncode=returncode, stdout=stdout, stderr=stderr)
            self.logger.debug(f"Signal 'alembic_command_completed' sent for command '{command}'.")
        else:
            self.dispatcher.send("alembic_command_failed", sender=self, command=command, args=args, 
                                returncode=returncode, stdout=stdout, stderr=stderr, 
                                error_type=error_type, exception=exception)
            self.logger.debug(f"Signal 'alembic_command_failed' sent for command '{command}'. Error Type: {error_type}.")

        return success, stdout, stderr

    # ============================================================================
    # Core Migration Operations
    # ============================================================================

    def makemigrations(self, message: str = "auto", **kwargs):
        """
        Creates a new migration script based on model changes using Alembic.
        
        Args:
            message: Migration message/description
            **kwargs: Additional options:
                - empty: Create empty migration
                - sql: Use SQL mode
                - head: Specify head to use
                - splice: Allow branch
                - branch_label: Branch label
                - version_path: Version path
                - rev_id: Revision ID
        """
        self.logger.info("Creating new migration script...")
        self.dispatcher.send("migration_makemigrations_command", sender=self, message=message, options=kwargs)
        
        args = []
        
        if kwargs.get('empty', False):
            pass
        else:
            args.append("--autogenerate")
        
        if message and message != "auto":
            args.extend(["-m", message])
        
        if kwargs.get('head'):
            args.extend(["--head", kwargs['head']])
        
        if kwargs.get('splice', False):
            args.append("--splice")
        
        if kwargs.get('branch_label'):
            args.extend(["--branch-label", kwargs['branch_label']])
        
        if kwargs.get('version_path'):
            args.extend(["--version-path", kwargs['version_path']])
        
        if kwargs.get('rev_id'):
            args.extend(["--rev-id", kwargs['rev_id']])
        
        if kwargs.get('sql', False):
            args.append("--sql")

        success, stdout, stderr = self._run_alembic("revision", *args)
        return success

    def migrate(self, version: str = "head", **kwargs):
        """
        Applies pending migrations to the database using Alembic.
        
        Args:
            version: Target version (head, version hash, or relative like +2, -1)
            **kwargs: Additional options:
                - sql: Generate SQL instead of executing
                - tag: Arbitrary tag to apply
        """
        self.logger.info(f"Applying migrations up to version: {version}")
        self.dispatcher.send("migration_migrate_command", sender=self, version=version, options=kwargs)

        args = [version]
        
        if kwargs.get('sql', False):
            args.append("--sql")
        
        if kwargs.get('tag'):
            args.extend(["--tag", kwargs['tag']])

        success, stdout, stderr = self._run_alembic("upgrade", *args)
        return success

    def rollback(self, version: str = "-1", **kwargs):
        """
        Rolls back migrations using Alembic.
        
        Args:
            version: Target version to rollback to
            **kwargs: Additional options:
                - sql: Generate SQL instead of executing
                - tag: Arbitrary tag to apply
        """
        self.logger.info(f"Rolling back migrations to version: {version}")
        self.dispatcher.send("migration_rollback_command", sender=self, version=version, options=kwargs)

        args = [version]
        
        if kwargs.get('sql', False):
            args.append("--sql")
        
        if kwargs.get('tag'):
            args.extend(["--tag", kwargs['tag']])

        success, stdout, stderr = self._run_alembic("downgrade", *args)
        return success

    # ============================================================================
    # Information & Status Commands
    # ============================================================================

    def history(self, **kwargs):
        """
        Shows the migration history using Alembic.
        
        Args:
            **kwargs: Additional options:
                - range: Range of revisions (e.g., "base:head")
                - verbose: Show full information
                - indicate_current: Indicate current revision
        """
        self.logger.info("Showing migration history...")
        self.dispatcher.send("migration_history_command", sender=self, options=kwargs)

        args = []
        
        if kwargs.get('range'):
            args.extend(["-r", kwargs['range']])
        
        if kwargs.get('verbose', False):
            args.append("--verbose")
        
        if kwargs.get('indicate_current', True):
            args.append("-i")

        success, stdout, stderr = self._run_alembic("history", *args)
        return success

    def current(self, **kwargs):
        """
        Shows current migration revision.
        
        Args:
            **kwargs: Additional options:
                - verbose: Show full information
        """
        self.logger.info("Showing current migration revision...")
        self.dispatcher.send("migration_current_command", sender=self, options=kwargs)

        args = []
        if kwargs.get('verbose', False):
            args.append("--verbose")

        success, stdout, stderr = self._run_alembic("current", *args)
        return success

    def show(self, revision: str, **kwargs):
        """
        Show details of a specific revision.
        
        Args:
            revision: Revision to show details for
            **kwargs: Additional options
        """
        self.logger.info(f"Showing details for revision: {revision}")
        self.dispatcher.send("migration_show_command", sender=self, revision=revision, options=kwargs)

        success, stdout, stderr = self._run_alembic("show", revision)
        return success

    def heads(self, **kwargs):
        """
        Show current heads in the migration tree.
        
        Args:
            **kwargs: Additional options:
                - verbose: Show full information
                - resolve_dependencies: Resolve dependencies
        """
        self.logger.info("Showing migration heads...")
        self.dispatcher.send("migration_heads_command", sender=self, options=kwargs)

        args = []
        if kwargs.get('verbose', False):
            args.append("--verbose")
        
        if kwargs.get('resolve_dependencies', False):
            args.append("--resolve-dependencies")

        success, stdout, stderr = self._run_alembic("heads", *args)
        return success

    def branches(self, **kwargs):
        """
        Show current branches in the migration tree.
        
        Args:
            **kwargs: Additional options:
                - verbose: Show full information
        """
        self.logger.info("Showing migration branches...")
        self.dispatcher.send("migration_branches_command", sender=self, options=kwargs)

        args = []
        if kwargs.get('verbose', False):
            args.append("--verbose")

        success, stdout, stderr = self._run_alembic("branches", *args)
        return success

    # ============================================================================
    # Advanced Operations
    # ============================================================================

    def stamp(self, revision: str, **kwargs):
        """
        Stamp the revision table with a specific revision without running migrations.
        
        Args:
            revision: Revision to stamp
            **kwargs: Additional options:
                - sql: Generate SQL instead of executing
                - tag: Arbitrary tag to apply
        """
        self.logger.info(f"Stamping database with revision: {revision}")
        self.dispatcher.send("migration_stamp_command", sender=self, revision=revision, options=kwargs)

        args = [revision]
        
        if kwargs.get('sql', False):
            args.append("--sql")
        
        if kwargs.get('tag'):
            args.extend(["--tag", kwargs['tag']])

        success, stdout, stderr = self._run_alembic("stamp", *args)
        return success

    def merge(self, *revisions, **kwargs):
        """
        Merge multiple revision heads into a single head.
        
        Args:
            *revisions: Revisions to merge
            **kwargs: Additional options:
                - message: Merge message
                - branch_label: Branch label
                - rev_id: Revision ID
        """
        self.logger.info(f"Merging revisions: {', '.join(revisions)}")
        self.dispatcher.send("migration_merge_command", sender=self, revisions=revisions, options=kwargs)

        args = list(revisions)
        
        if kwargs.get('message'):
            args.extend(["-m", kwargs['message']])
        
        if kwargs.get('branch_label'):
            args.extend(["--branch-label", kwargs['branch_label']])
        
        if kwargs.get('rev_id'):
            args.extend(["--rev-id", kwargs['rev_id']])

        success, stdout, stderr = self._run_alembic("merge", *args)
        return success

    def squash(self, start_revision: str, end_revision: str = "head", **kwargs):
        """
        Squash multiple migrations into a single migration.
        Note: This requires manual implementation as Alembic doesn't have native squash.
        """
        self.logger.info(f"Squashing migrations from {start_revision} to {end_revision}")
        self.dispatcher.send("migration_squash_command", sender=self, 
                           start_revision=start_revision, end_revision=end_revision, options=kwargs)
        
        self.logger.warning("Squash functionality requires manual implementation")
        print("Note: Migration squashing requires manual consolidation of migration files.")
        return False

    # ============================================================================
    # Database Operations
    # ============================================================================

    def check(self):
        """
        Check if there are pending migrations.
        """
        self.logger.info("Checking for pending migrations...")
        self.dispatcher.send("migration_check_command", sender=self)

        success, stdout, stderr = self._run_alembic("current", capture_output=True)
        if not success:
            return False

        current_success, current_out, _ = self._run_alembic("current", capture_output=True)
        heads_success, heads_out, _ = self._run_alembic("heads", capture_output=True)
        
        if current_success and heads_success:
            current_rev = current_out.strip()
            head_rev = heads_out.strip()
            
            if current_rev == head_rev:
                print("Database is up to date")
                return True
            else:
                print("Database has pending migrations")
                return False
        
        return False

    def validate(self):
        """
        Validate current migration state.
        """
        self.logger.info("Validating migration state...")
        self.dispatcher.send("migration_validate_command", sender=self)

        success, stdout, stderr = self._run_alembic("current", capture_output=True)
        if not success:
            print("Failed to get current migration state")
            return False

        success, stdout, stderr = self._run_alembic("branches", capture_output=True)
        if success and stdout:
            branches = [line.strip() for line in stdout.split('\n') if line.strip()]
            if len(branches) > 1:
                print("Multiple migration branches detected:")
                for branch in branches:
                    print(f"  - {branch}")
            else:
                print("No orphaned branches found")

        print("Migration state validation completed")
        return True

    # ============================================================================
    # Utility Operations
    # ============================================================================

    def reset(self, **kwargs):
        """
        Reset database to base state (downgrade to base).
        
        Args:
            **kwargs: Additional options:
                - confirm: Skip confirmation prompt
        """
        if not kwargs.get('confirm', False):
            response = input("WARNING: This will reset the database to base state. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Reset cancelled.")
                return False

        self.logger.info("Resetting database to base state...")
        self.dispatcher.send("migration_reset_command", sender=self, options=kwargs)

        success, stdout, stderr = self._run_alembic("downgrade", "base")
        if success:
            print("Database reset to base state")
        return success

    def fresh(self, **kwargs):
        """
        Reset database and apply all migrations (fresh start).
        
        Args:
            **kwargs: Additional options:
                - confirm: Skip confirmation prompt
        """
        if not kwargs.get('confirm', False):
            response = input("WARNING: This will reset and re-apply all migrations. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Fresh migration cancelled.")
                return False

        self.logger.info("Performing fresh migration...")
        self.dispatcher.send("migration_fresh_command", sender=self, options=kwargs)

        success = self.reset(confirm=True)
        if not success:
            return False

        success = self.migrate("head")
        if success:
            print("Fresh migration completed")
        return success

    def clean(self, **kwargs):
        """
        Clean up migration files and cache.
        
        Args:
            **kwargs: Additional options:
                - confirm: Skip confirmation prompt
                - cache_only: Only clean cache, not migrations
        """
        if not kwargs.get('confirm', False):
            response = input("WARNING: This will clean migration cache. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Clean cancelled.")
                return False

        self.logger.info("Cleaning migration cache...")
        self.dispatcher.send("migration_clean_command", sender=self, options=kwargs)

        try:
            cache_dir = Path(self.config.project_root) / ".alembic_cache"
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                print("Migration cache cleaned")

            versions_dir = Path(self.config.project_root) / "alembic" / "versions"
            if versions_dir.exists():
                pycache_dir = versions_dir / "__pycache__"
                if pycache_dir.exists():
                    import shutil
                    shutil.rmtree(pycache_dir)
                    print("Migration bytecode cache cleaned")

            return True

        except Exception as e:
            self.logger.error(f"Failed to clean migration cache: {e}")
            print(f"Failed to clean cache: {e}")
            return False

    def status(self):
        """
        Show comprehensive migration status.
        """
        self.logger.info("Showing migration status...")
        self.dispatcher.send("migration_status_command", sender=self)

        print("=== Migration Status ===")
        
        success, stdout, stderr = self._run_alembic("current", capture_output=True)
        if success:
            current = stdout.strip() or "None"
            print(f"Current revision: {current}")
        
        success, stdout, stderr = self._run_alembic("heads", capture_output=True)
        if success:
            head = stdout.strip() or "None"
            print(f"Head revision: {head}")
        
        success, stdout, stderr = self._run_alembic("history", "-r", "current:head", capture_output=True)
        if success and stdout:
            migrations = [line for line in stdout.split('\n') if line.strip()]
            pending_count = max(0, len(migrations) - 1)
            print(f"Pending migrations: {pending_count}")
        
        success, stdout, stderr = self._run_alembic("branches", capture_output=True)
        if success:
            branches = [line for line in stdout.split('\n') if line.strip()]
            print(f"Branch count: {len(branches)}")

        return True

    def list_migrations(self, **kwargs):
        """
        List all available migrations with details.
        
        Args:
            **kwargs: Additional options:
                - pending_only: Show only pending migrations
                - applied_only: Show only applied migrations
        """
        self.logger.info("Listing migrations...")
        self.dispatcher.send("migration_list_command", sender=self, options=kwargs)

        if kwargs.get('pending_only'):
            success, stdout, stderr = self._run_alembic("history", "-r", "current:head")
        elif kwargs.get('applied_only'):
            success, stdout, stderr = self._run_alembic("history", "-r", "base:current")
        else:
            success, stdout, stderr = self._run_alembic("history", "-i")

        return success