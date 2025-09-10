"""
Kiro Steering Initializer

Adds `.kiro/steering/super_kiro.md` and `.kiro/super_kiro/commands/*` into a target directory.

Usage (via SuperKiro CLI):
  SuperKiro kiro-init [target_dir] [--force]

Notes:
- Treat '~' as the current workspace root (PWD), not OS home.
- By default, existing files are not overwritten unless --force is specified.
"""

import argparse
from pathlib import Path
from typing import Optional, Tuple

from ...utils.ui import display_info, display_success, display_warning, display_error


def register_parser(subparsers, global_parser=None) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "kiro-init",
        help="Initialize Kiro steering in a directory (.kiro) — replaces existing managed files",
        parents=[global_parser] if global_parser else [],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Copy Kiro steering templates into the target directory.\n\n"
            "Examples:\n"
            "  SuperKiro kiro-init                # install into current dir (overwrite managed files)\n"
            "  SuperKiro kiro-init ..             # install into parent dir\n"
            "  SuperKiro kiro-init ~              # treat ~ as workspace root (PWD)\n"
            "  SuperKiro kiro-init . --force      # overwrite existing files\n"
            "  SuperKiro kiro-init . --prune      # remove SuperKiro-managed files (.kiro/steering/super_kiro.md and .kiro/super_kiro/*)\n"
            "  SuperKiro kiro-init . --sync       # prune then re-copy latest templates\n"
            "  SuperKiro kiro-init . --only-commands   # install command templates only (super_kiro.md always included)\n"
            "  SuperKiro kiro-init . --only-agents     # install agent persona templates only (super_kiro.md always included)\n"
        ),
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    # Use global --force flag
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove only SuperKiro-managed steering files from the target (.kiro/steering/super_kiro.md and .kiro/super_kiro)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Prune SuperKiro-managed templates then copy the latest templates"
    )
    parser.add_argument(
        "--only-commands",
        action="store_true",
        help="Install only command templates (.kiro/super_kiro/commands); super_kiro.md always included"
    )
    parser.add_argument(
        "--only-agents",
        action="store_true",
        help="Install only agent persona templates (.kiro/steering/sk_*.md); super_kiro.md always included"
    )
    return parser


def _resolve_target(target_dir: str) -> Path:
    # Treat '~' as the current workspace root (PWD), not OS home
    if target_dir.strip() == "~":
        return Path.cwd()
    return Path(target_dir).resolve()


def _get_template_root() -> Path:
    """Resolve template source root (package resources if available, otherwise filesystem fallback)."""
    # Try Python 3.9+ importlib.resources.files
    try:
        from importlib.resources import files as ir_files  # type: ignore
        return ir_files("setup.templates.kiro.steering")
    except Exception:
        # Fallback to repository filesystem path
        repo_setup_root = Path(__file__).resolve().parents[2]
        fs_root = repo_setup_root / "templates" / "kiro" / "steering"
        return fs_root


def _iter_md_files(base: Path):
    for entry in base.rglob("*"):
        try:
            if entry.is_file() and entry.name.endswith(".md"):
                yield entry
        except Exception:
            continue


def _copy_templates(dest: Path, force: bool, *, only_commands: bool = False, only_agents: bool = False) -> Tuple[int, int]:
    """Copy steering templates from package data to destination.

    Returns (written_count, skipped_count).
    """
    pkg_root = _get_template_root()
    if not pkg_root.exists():
        display_error(f"Template source not found: {pkg_root}")
        return (0, 0)

    # Destination layout:
    # - .kiro/steering/super_kiro.md (top-level overview)
    # - .kiro/super_kiro/commands/*.md (all command templates)
    base_root = dest.parent  # .kiro
    steering_dir = base_root / "steering"
    commands_dir = base_root / "super_kiro" / "commands"
    steering_dir.mkdir(parents=True, exist_ok=True)
    commands_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for src in _iter_md_files(pkg_root):
        rel = src.relative_to(pkg_root)
        # Categorize
        is_super = (rel.as_posix() == "super_kiro.md")
        is_command = (len(rel.parts) > 0 and rel.parts[0] == "commands")
        is_agent = (not is_command and not is_super)

        # Filter by requested categories (super_kiro.md is always included)
        if not is_super:
            if only_commands and not is_command:
                continue
            if only_agents and not is_agent:
                continue

        # Route files based on their location inside the template tree
        if is_command:
            # commands/* -> .kiro/super_kiro/commands/*
            subrel = Path(*rel.parts[1:]) if len(rel.parts) > 1 else Path()
            dst = commands_dir / subrel.as_posix()
        else:
            # super_kiro.md (and any future top-level) -> .kiro/steering/
            dst = steering_dir / rel.as_posix()
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not force:
            display_warning(f"[SKIP] {dst} exists (use --force to overwrite)")
            skipped += 1
            continue
        try:
            content = src.read_text(encoding="utf-8")
            dst.write_text(content, encoding="utf-8")
            display_info(f"[WRITE] {dst}")
            written += 1
        except FileNotFoundError:
            display_error(f"Template not found: {src}")
        except Exception as e:
            display_error(f"Failed to write {dst}: {e}")
    return (written, skipped)


def _prune_templates(dest: Path) -> Tuple[int, int]:
    """Remove only SuperKiro-managed template files from dest.

    Returns (removed_count, preserved_count).
    """
    pkg_root = _get_template_root()
    if not pkg_root.exists():
        display_error(f"Template source not found: {pkg_root}")
        return (0, 0)

    removed = 0
    preserved = 0

    base_root = dest.parent  # .kiro
    steering_dir = base_root / "steering"
    commands_dir = base_root / "super_kiro" / "commands"

    # Build concrete target paths mapped from templates
    for src in _iter_md_files(pkg_root):
        rel = src.relative_to(pkg_root)
        if rel.parts[0] == "commands":
            subrel = Path(*rel.parts[1:]) if len(rel.parts) > 1 else Path()
            target = commands_dir / subrel.as_posix()
        else:
            target = steering_dir / rel.as_posix()

        try:
            if target.exists():
                target.unlink()
                display_info(f"[REMOVE] {target}")
                removed += 1
            else:
                preserved += 1
        except Exception as e:
            display_warning(f"Could not remove {target}: {e}")

    # Clean up empty new-structure directories
    try:
        if commands_dir.exists() and not any(commands_dir.rglob("*")):
            commands_dir.rmdir()
            display_info(f"[REMOVE] {commands_dir} (empty)")
        superkiro_dir = commands_dir.parent
        if superkiro_dir.exists() and not any(superkiro_dir.rglob("*")):
            superkiro_dir.rmdir()
            display_info(f"[REMOVE] {superkiro_dir} (empty)")
    except Exception:
        pass

    return (removed, preserved)



def run(args: argparse.Namespace) -> int:
    target_root = _resolve_target(getattr(args, "target_dir", "."))
    dest = target_root / ".kiro" / "steering"

    display_info(f"Initializing Kiro steering into: {dest}")
    # Default behavior: full replace of managed files
    force = True

    # Prune-only mode
    if getattr(args, "prune", False) and not getattr(args, "sync", False):
        removed, preserved = _prune_templates(dest)
        display_success(f"Kiro steering prune complete: {removed} removed, {preserved} preserved")
        return 0

    # Sync mode: prune then copy latest
    if getattr(args, "sync", False):
        only_commands = bool(getattr(args, "only_commands", False))
        only_agents = bool(getattr(args, "only_agents", False))
        _prune_templates(dest)
        written, skipped = _copy_templates(dest, force=True, only_commands=only_commands, only_agents=only_agents)
        display_success(f"Kiro steering sync complete: {written} written")
        return 0

    # Default: full replace (prune then copy)
    only_commands = bool(getattr(args, "only_commands", False))
    only_agents = bool(getattr(args, "only_agents", False))
    _prune_templates(dest)
    written, skipped = _copy_templates(dest, force=True, only_commands=only_commands, only_agents=only_agents)
    display_success(f"Kiro steering init complete: {written} written (existing managed files replaced)")
    return 0
