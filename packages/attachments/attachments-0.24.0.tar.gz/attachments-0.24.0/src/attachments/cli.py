#!/usr/bin/env python3
"""
attachments.cli - "att" / "attachments" command-line interface

USAGE
  att [OPTIONS] [PATH...] [DSL_OPTIONS...]
  att . --glob **/*.py --clipboard --mode report --prompt "What files should we look into"
  att . --glob **/*.py --clipboard --prompt "Find the bug"
  att --copy report.pdf --pages 1-4
  att presentation.pptx[pages:1-5][images:false] data.csv[limit:100]

OPTIONS
  -c, -y, --copy, --clipboard       Copy result to clipboard
  -f, --files                       Append [files:true] to DSL
  -v, --verbose                     Enable library log output
  --help                            Show this help

DSL OPTIONS
  --pages N-M             Select page range (or file.pdf[pages:N-M])
  --prompt TEXT           Add prompt before the Attchements for the LLM to see
  --KEY[=VALUE]           Arbitrary DSL: becomes [key:value]

Note: Running 'att' with no arguments shows this help and exits.
"""

from __future__ import annotations

import os
import re
import sys

import typer

from . import Attachments, set_verbose

###############################################################################
# internal helpers
###############################################################################


def _resolve_path(path: str) -> str:
    """
    Resolve special paths like '.' to actual paths.

    Parameters
    ----------
    path : str
        Path that might be '.' or other special values

    Returns
    -------
    str
        Resolved path
    """
    if path == "." or path == "./":
        return os.getcwd()
    return path


def _extract_dsl_from_path(path: str) -> tuple[str, str]:
    """
    Extract DSL notation from a path if present.

    Returns
    -------
    (clean_path, dsl_fragment)

    Examples
    --------
    'file.pdf[pages:1-4]' → ('file.pdf', '[pages:1-4]')
    'file.pdf' → ('file.pdf', '')
    """
    # Find the first [ that starts a DSL fragment
    match = re.search(r"^([^\[]+)(\[.+\])$", path)
    if match:
        return match.group(1), match.group(2)
    return path, ""


def _parse_mixed_args(args: list[str]) -> tuple[list[str], dict[str, str | list[str]]]:
    """
    Parse a mixed list of paths and flags, extracting them separately.

    Handles:
    - Paths with embedded DSL: file.pdf[pages:1-4]
    - Flags anywhere: --pages 1-4, --copy, -c
    - Mixed ordering: att --copy file.pdf --pages 1-4 file2.docx

    Returns
    -------
    (paths, flag_dict)
    """
    paths = []
    flags: dict[str, str | list[str]] = {}

    i = 0
    while i < len(args):
        arg = args[i]

        # Check if it's a flag (starts with - or --)
        if arg.startswith("-"):
            # Extract flag name
            flag_name = arg.lstrip("-")

            # Handle different flag formats
            if "=" in flag_name:
                # Format: --key=value
                key, value = flag_name.split("=", 1)
                _add_flag_value(flags, key, value)
            elif flag_name in ["c", "y", "copy", "v", "verbose", "f", "files", "clipboard"]:
                # Boolean flags
                if flag_name in ["c", "y", "clipboard", "copy"]:
                    flags["copy"] = "true"
                elif flag_name in ["v", "verbose"]:
                    flags["verbose"] = "true"
                elif flag_name in ["f", "files"]:
                    flags["files"] = "true"
                else:
                    flags[flag_name] = "true"
            elif i + 1 < len(args) and not args[i + 1].startswith("-"):
                # Format: --key value
                value = args[i + 1]
                i += 1  # Skip the value in next iteration
                _add_flag_value(flags, flag_name, value)
            else:
                # Flag without value
                flags[flag_name] = "true"
        else:
            # It's a path
            paths.append(arg)

        i += 1

    return paths, flags


def _add_flag_value(flags: dict[str, str | list[str]], key: str, value: str) -> None:
    """
    Add a flag value to the flags dictionary, handling repeated keys properly.
    """
    # Handle comma-separated values in a single argument
    if "," in value:
        values = [v.strip() for v in value.split(",")]
        if key in flags:
            if isinstance(flags[key], list):
                flags[key].extend(values)
            else:
                flags[key] = [flags[key]] + values
        else:
            flags[key] = values if len(values) > 1 else values[0]
    else:
        # Single value
        if key in flags:
            if isinstance(flags[key], list):
                flags[key].append(value)
            else:
                flags[key] = [flags[key], value]
        else:
            flags[key] = value


def _build_dsl_from_flags(flags: dict[str, str | list[str]], exclude_keys: set[str] = None) -> str:
    """
    Convert flag dictionary to DSL fragment string.

    Parameters
    ----------
    flags : dict
        Dictionary of flags and their values
    exclude_keys : set
        Keys to exclude from DSL generation (e.g., 'copy', 'verbose', 'prompt')

    Returns
    -------
    str
        DSL fragment like '[pages:1-4][lang:en]'
    """
    if exclude_keys is None:
        exclude_keys = {"c", "y", "f", "help", "h", "copy", "verbose", "clipboard"}

    dsl_parts = []
    for key, value in flags.items():
        if key in exclude_keys:
            continue

        if isinstance(value, list):
            # Join multiple values with comma
            dsl_parts.append(f"[{key}:{','.join(str(v) for v in value)}]")
        else:
            dsl_parts.append(f"[{key}:{value}]")

    return "".join(dsl_parts)


def _show_help():
    """Display help message."""
    typer.echo(__doc__)
    typer.echo(
        "\n🚀  Quick Start Examples\n"
        "═══════════════════════\n\n"
        "  Tree view of current directory:\n"
        "    ❯ att .\n\n"
        "  Copy directory tree with prompt:\n"
        '    ❯ att . -c --prompt "Which file should I look at?"\n\n'
        "  Extract specific pages (two ways):\n"
        "    ❯ att report.pdf --pages 1-4\n"
        "    ❯ att report.pdf[pages:1-4]\n\n"
        "  Process multiple files:\n"
        "    ❯ att file1.pptx[pages:1-5] file2.csv --copy\n\n"
        "  Flexible ordering (flags anywhere!):\n"
        "    ❯ att --copy report.pdf --pages 1-4 data.csv\n"
        "    ❯ att -v file.pdf[pages:1-3] --lang en -c\n\n"
        "\n📖  Core Options\n"
        "══════════════\n\n"
        "  -c, -y, --copy, --clipboard     Copy result to clipboard\n"
        "  -v, --verbose                   Enable debug output\n"
        "  -f, --files                     Force directory expansion\n"
        '  --prompt "..."                  Add prompt when copying\n'
        "  --help                          Show this help message\n\n"
        "\n🎯  DSL Reference\n"
        "═══════════════\n\n"
        "  Common DSL options (use with --flag or [flag:value]):\n"
        "  • pages/slides: 1-4, 1,3,5, -1 (last page)\n"
        "  • images: true/false (include/exclude images)\n"
        "  • format: plain, markdown (text format)\n"
        "  • select: CSS selector for web pages\n"
        "  • limit: Row limit for CSV files\n"
        "  • summary: true for DataFrame summaries\n"
        "  • rotate: Degrees for image rotation\n"
        "  • crop: x,y,width,height for images\n"
        "  • viewport: widthxheight for screenshots\n"
        "  • truncate: Maximum characters\n"
        "  • ignore: Patterns to ignore (comma-separated or multiple flags)\n"
        "  • glob: File patterns to match\n"
        "  • mode: Processing mode (report, structure, etc.)\n"
        "  • And many more...\n\n"
        "  📚 Full docs: https://maximerivest.github.io/attachments/\n"
    )


###############################################################################
# Main entry point
###############################################################################


def app() -> None:
    """Process command line arguments and execute attachments."""
    # Get all command line arguments (skip the script name)
    args = sys.argv[1:]

    # Show help if no arguments or help flag
    if not args or any(arg in ["--help", "-h", "help"] for arg in args):
        _show_help()
        sys.exit(0)

    # Parse mixed arguments
    paths, flags = _parse_mixed_args(args)

    # Show what we're processing in a subtle, appealing way
    path_display = ", ".join(paths[:2]) + ("..." if len(paths) > 2 else "")
    typer.secho(f"🔍 {path_display}", fg=typer.colors.BRIGHT_BLACK, dim=True)

    # Show non-control DSL flags if any
    dsl_flags = {k: v for k, v in flags.items() if k not in {"copy", "verbose", "files"}}
    if dsl_flags:
        flag_display = " ".join([f"{k}:{v}" if v != "true" else k for k, v in dsl_flags.items()])
        typer.secho(f"⚙️  {flag_display}", fg=typer.colors.BRIGHT_BLACK, dim=True)

    # Extract control flags
    verbose = flags.get("verbose", "false") == "true"
    copy = flags.get("copy", "false") == "true"

    # Set verbosity
    set_verbose(verbose)

    # Build DSL from remaining flags
    dsl_from_flags = _build_dsl_from_flags(flags)

    # Process paths, extracting embedded DSL and combining with flag DSL
    processed_paths = []
    for path in paths:
        # Resolve special paths like '.'
        resolved_path = _resolve_path(path)
        clean_path, embedded_dsl = _extract_dsl_from_path(resolved_path)
        # Combine embedded DSL with flag DSL (embedded takes precedence)
        combined_dsl = embedded_dsl + dsl_from_flags
        processed_paths.append(clean_path + combined_dsl)

    # Execute
    if not processed_paths:
        typer.secho("❌  Error: No paths provided", fg=typer.colors.RED, err=True)
        typer.echo("\n💡 Tip: Use '.' for current directory or provide file paths")
        typer.echo("\n📖 For help: att --help")
        sys.exit(1)

    if "prompt" in flags.keys() and not copy:
        typer.secho("❌  Error: Prompt without copy is ignored", fg=typer.colors.RED, err=True)

    try:
        result = Attachments(*processed_paths)

        if copy:
            # Copy to clipboard with optional prompt
            result.to_clipboard_text(flags.get("prompt", ""))
            # The clipboard function already prints a message, so we don't need to print again
        else:
            # Output to terminal
            typer.echo(result.text)

    except Exception as exc:  # noqa: BLE001
        typer.secho(f"❌  Error: {exc}", fg=typer.colors.RED, err=True)

        # Provide helpful suggestions based on common errors
        error_msg = str(exc).lower()
        if "no such file" in error_msg or "not found" in error_msg:
            typer.echo("\n💡 Tip: Check that the file path is correct")
            typer.echo("        Use '.' for current directory")
        elif "invalid dsl" in error_msg or "invalid syntax" in error_msg:
            typer.echo("\n💡 Tip: Check DSL syntax")
            typer.echo("        ✓ Correct: [pages:1-4]")
            typer.echo("        ✗ Wrong:   [pages: 1-4] (no spaces)")
        elif "permission" in error_msg:
            typer.echo("\n💡 Tip: Check file permissions")

        sys.exit(1)
    finally:
        # Always reset verbosity
        set_verbose(False)


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app()
