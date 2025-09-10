#!/usr/bin/env python3
"""
Framework Management Hub
Unified entry point for framework operations.

Examples (program name adapts to invocation):
    SuperKiro install [options]
    SuperKiro update [options]
    SuperKiro uninstall [options]
    SuperKiro backup [options]
    SuperKiro --help
"""

import sys
import argparse
import subprocess
import difflib
from pathlib import Path
from typing import Dict, Callable

# Add the local 'setup' directory to the Python import path
current_dir = Path(__file__).parent
project_root = current_dir.parent
setup_dir = project_root / "setup"

# Insert the setup directory at the beginning of sys.path
if setup_dir.exists():
    sys.path.insert(0, str(setup_dir.parent))
else:
    print(f"Warning: Setup directory not found at {setup_dir}")
    sys.exit(1)


# Try to import utilities from the setup package
try:
    from setup.utils.ui import (
        display_header, display_info, display_success, display_error,
        display_warning, Colors
    )
    from setup.utils.logger import setup_logging, get_logger, LogLevel
    from setup import DEFAULT_INSTALL_DIR
except ImportError:
    # Provide minimal fallback functions and constants if imports fail
    class Colors:
        RED = YELLOW = GREEN = CYAN = RESET = ""

    def display_error(msg): print(f"[ERROR] {msg}")
    def display_warning(msg): print(f"[WARN] {msg}")
    def display_success(msg): print(f"[OK] {msg}")
    def display_info(msg): print(f"[INFO] {msg}")
    def display_header(title, subtitle): print(f"{title} - {subtitle}")
    def get_logger(): return None
    def setup_logging(*args, **kwargs): pass
    class LogLevel:
        ERROR = 40
        INFO = 20
        DEBUG = 10


def create_global_parser() -> argparse.ArgumentParser:
    """Create shared parser for global flags used by all commands"""
    global_parser = argparse.ArgumentParser(add_help=False)

    global_parser.add_argument("--verbose", "-v", action="store_true",
                               help="Enable verbose logging")
    global_parser.add_argument("--quiet", "-q", action="store_true",
                               help="Suppress all output except errors")
    global_parser.add_argument("--install-dir", type=Path, default=DEFAULT_INSTALL_DIR,
                               help=f"Target installation directory (default: {DEFAULT_INSTALL_DIR})")
    global_parser.add_argument("--dry-run", action="store_true",
                               help="Simulate operation without making changes")
    global_parser.add_argument("--force", action="store_true",
                               help="Force execution, skipping checks")
    global_parser.add_argument("--yes", "-y", action="store_true",
                               help="Automatically answer yes to all prompts")
    global_parser.add_argument("--no-update-check", action="store_true",
                               help="Skip checking for updates")
    global_parser.add_argument("--auto-update", action="store_true",
                               help="Automatically install updates without prompting")

    return global_parser


def _detect_program_name() -> str:
    """Return branded program name.
    Since this package is SuperKiro-only, always return 'SuperKiro'.
    """
    return "SuperKiro"


def create_parser():
    """Create the main CLI parser and attach subcommand parsers"""
    global_parser = create_global_parser()

    PROGRAM_NAME = _detect_program_name()

    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=f"{PROGRAM_NAME} Framework Management Hub - Unified CLI",
        epilog="""
Examples:
  {prog} install --dry-run
  {prog} update --verbose
  {prog} backup --create
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[global_parser]
    )
    # format epilog with the detected program name
    parser.epilog = parser.epilog.format(prog=PROGRAM_NAME)

    from SuperKiro import __version__
    parser.add_argument("--version", action="version", version=f"SuperKiro {__version__}")

    subparsers = parser.add_subparsers(
        dest="operation",
        title="Operations",
        description="Framework operations to perform"
    )

    return parser, subparsers, global_parser


def setup_global_environment(args: argparse.Namespace):
    """Set up logging and shared runtime environment based on args"""
    # Determine log level
    if args.quiet:
        level = LogLevel.ERROR
    elif args.verbose:
        level = LogLevel.DEBUG
    else:
        level = LogLevel.INFO

    # Define log directory unless it's a dry run
    log_dir = args.install_dir / "logs" if not args.dry_run else None
    setup_logging("superkiro_hub", log_dir=log_dir, console_level=level)

    # Log startup context
    logger = get_logger()
    if logger:
        logger.debug(f"SuperKiro called with operation: {getattr(args, 'operation', 'None')}")
        logger.debug(f"Arguments: {vars(args)}")


def get_operation_modules() -> Dict[str, str]:
    """Return supported operations and their descriptions"""
    return {
        "install": "Initialize .kiro steering (.kiro/steering/super_kiro.md) and .kiro/super_kiro/commands (alias of kiro-init)",
        "update": "Update existing SuperKiro installation",
        "uninstall": "Remove SuperKiro installation",
        "backup": "Backup and restore operations",
        "kiro-init": "Initialize .kiro steering: super_kiro.md + super_kiro/commands"
    }


def load_operation_module(name: str):
    """Try to dynamically import an operation module"""
    try:
        sanitized = name.replace('-', '_')
        return __import__(f"setup.cli.commands.{sanitized}", fromlist=[sanitized])
    except ImportError as e:
            logger = get_logger()
            if logger:
                logger.error(f"Module '{name}' failed to load: {e}")
            return None


def register_operation_parsers(subparsers, global_parser) -> Dict[str, Callable]:
    """Register subcommand parsers and map operation names to their run functions"""
    operations = {}
    for name, desc in get_operation_modules().items():
        module = load_operation_module(name)
        if module and hasattr(module, 'register_parser') and hasattr(module, 'run'):
            module.register_parser(subparsers, global_parser)
            operations[name] = module.run
        else:
            # If module doesn't exist, register a stub parser that will error at runtime
            subparsers.add_parser(name, help=f"{desc}", parents=[global_parser])
            operations[name] = None
    return operations


def main() -> int:
    """Main entry point"""
    try:
        parser, subparsers, global_parser = create_parser()
        operations = register_operation_parsers(subparsers, global_parser)
        args = parser.parse_args()
        
        # Check for updates unless disabled
        if not args.quiet and not getattr(args, 'no_update_check', False):
            try:
                from setup.utils.updater import check_for_updates
                # Check for updates in the background
                from SuperKiro import __version__
                updated = check_for_updates(
                    current_version=__version__,
                    auto_update=getattr(args, 'auto_update', False)
                )
                # If updated, suggest restart
                if updated:
                    print("\n🔄 {} was updated. Please restart to use the new version.".format(_detect_program_name()))
            except ImportError:
                # Updater module not available, skip silently
                pass
            except Exception:
                # Any other error, skip silently
                pass

        # No operation provided? Show help manually unless in quiet mode
        if not args.operation:
            if not args.quiet:
                from SuperKiro import __version__
                display_header(f"{_detect_program_name()} Framework v{__version__}", "Unified CLI for all operations")
                print(f"{Colors.CYAN}Available operations:{Colors.RESET}")
                for op, desc in get_operation_modules().items():
                    print(f"  {op:<12} {desc}")
            return 0

        # Handle unknown operations and suggest corrections
        if args.operation not in operations:
            close = difflib.get_close_matches(args.operation, operations.keys(), n=1)
            suggestion = f"Did you mean: {close[0]}?" if close else ""
            display_error(f"Unknown operation: '{args.operation}'. {suggestion}")
            return 1

        # Setup global context (logging, install path, etc.)
        setup_global_environment(args)
        logger = get_logger()

        # Execute operation
        run_func = operations.get(args.operation)
        if run_func:
            if logger:
                logger.info(f"Executing operation: {args.operation}")
            return run_func(args)
        else:
            # No module available and no legacy fallback supported
            display_error(f"Operation '{args.operation}' is not available in this version.")
            return 1

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
        return 130
    except Exception as e:
        try:
            logger = get_logger()
            if logger:
                logger.exception(f"Unhandled error: {e}")
        except:
            print(f"{Colors.RED}[ERROR] {e}{Colors.RESET}")
        return 1


# Entrypoint guard
if __name__ == "__main__":
    sys.exit(main())
    
