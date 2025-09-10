# This file contains logic for generating file reports with character and line counts.
# It processes directories and generates detailed reports about file contents.

import os

from attachments.core import Attachment, presenter
from attachments.pipelines import processor


def report_match(att: Attachment) -> bool:
    """Matches when the DSL command [mode:report] or [format:report] is present and it's a directory."""
    import os

    has_report_mode = att.commands.get("mode") == "report" or att.commands.get("format") == "report"
    is_directory = os.path.isdir(att.path)
    return has_report_mode and is_directory


@presenter
def file_report_presenter(att: Attachment, structure_obj: dict) -> Attachment:
    """Generates a detailed file report with character and line counts."""
    if not isinstance(structure_obj, dict) or structure_obj.get("type") not in (
        "directory",
        "git_repository",
    ):
        att.text = "Report presenter requires a directory or repository structure"
        return att

    files = structure_obj.get("files", [])
    base_path = structure_obj.get("path", "")

    if not files:
        att.text = "No files found to report on"
        return att

    # Collect file info with character and line counts
    file_info = []
    total_chars = 0
    total_lines = 0

    for file_path in files:
        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Get relative path
            if file_path.startswith(base_path):
                rel_path = os.path.relpath(file_path, base_path)
            else:
                rel_path = file_path

            # Count characters and lines
            chars = len(content)
            lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

            # Get file extension
            ext = os.path.splitext(rel_path)[1].lower() if "." in rel_path else "no-ext"

            file_info.append({"path": rel_path, "chars": chars, "lines": lines, "ext": ext})

            total_chars += chars
            total_lines += lines

        except Exception:
            # Skip files that can't be read
            continue

    # Sort by character count (descending)
    file_info.sort(key=lambda x: x["chars"], reverse=True)

    # Generate report
    report_lines = []
    report_lines.append("📊 File Report")
    report_lines.append("=" * 60)
    report_lines.append("")
    report_lines.append(
        f"Total: {len(file_info)} files, {total_chars:,} characters, {total_lines:,} lines"
    )
    report_lines.append("")

    # File details table
    report_lines.append("Characters |    Lines | Extension | File Path")
    report_lines.append("-" * 60)

    for info in file_info:
        chars = info["chars"]
        lines = info["lines"]
        ext = info["ext"]
        path = info["path"]

        chars_str = f"{chars:>9,}"
        lines_str = f"{lines:>7,}"
        ext_str = f"{ext:>8}"

        report_lines.append(f"{chars_str} | {lines_str} | {ext_str} | {path}")

    # Summary by file type
    report_lines.append("")
    report_lines.append("Summary by file type:")
    report_lines.append("-" * 50)

    ext_summary = {}
    for info in file_info:
        ext = info["ext"]
        if ext not in ext_summary:
            ext_summary[ext] = {"count": 0, "chars": 0, "lines": 0}
        ext_summary[ext]["count"] += 1
        ext_summary[ext]["chars"] += info["chars"]
        ext_summary[ext]["lines"] += info["lines"]

    # Sort by total characters
    for ext, data in sorted(ext_summary.items(), key=lambda x: x[1]["chars"], reverse=True):
        count = data["count"]
        chars = data["chars"]
        lines = data["lines"]
        avg_chars = chars // count if count > 0 else 0
        avg_lines = lines // count if count > 0 else 0

        percent = (chars / total_chars * 100) if total_chars > 0 else 0

        report_lines.append(
            f"{ext:>8}: {count:>2} files, {chars:>9,} chars, {lines:>7,} lines "
            f"(avg: {avg_chars:>6,}c/{avg_lines:>4,}l) {percent:>5.1f}%"
        )

    att.text = "\n".join(report_lines)
    return att


@processor(
    match=report_match,
    description="Generates detailed file reports with character and line counts for directories",
)
def report_to_llm(att: Attachment) -> Attachment:
    """Processes directories and generates file reports with character and line counts."""
    from attachments import load

    # Process as directory to get file structure, then manually call presenter
    att = att | load.directory_to_structure

    # Manually call the presenter with the structure object
    if att._obj is not None:
        result = file_report_presenter(att, att._obj)
        # Clear the _obj to prevent other presenters from running
        result._obj = None
        return result
    else:
        att.text = "No directory structure found to report on"
        return att
