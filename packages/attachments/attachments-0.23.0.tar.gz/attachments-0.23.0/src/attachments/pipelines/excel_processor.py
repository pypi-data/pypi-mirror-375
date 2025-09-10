"""
Excel to LLM Pipeline Processor
===============================

Complete pipeline for processing Excel files optimized for LLM consumption.
Supports clean DSL commands for the Attachments() simple API.

DSL Commands:
    [images:true|false] - Include sheet screenshots (default: true)
    [format:plain|markdown|csv] - Text formatting (default: markdown)
        Aliases: text=plain, txt=plain, md=markdown
    [pages:1-3,5] - Specific sheets (inherits from existing modify.pages, treats pages as sheets)
    [resize_images:50%|800x600] - Image resize specification (consistent naming)
    [tile:2x2|3x1|4] - Tile multiple sheets into grid layout (default: 2x2 for multi-sheet workbooks)

Note: Multi-sheet Excel files are automatically tiled in a 2x2 grid by default for better LLM consumption.
Use [tile:false] to disable tiling or [tile:3x1] for custom layouts.

Usage:
    # Explicit processor access
    result = processors.excel_to_llm(attach("workbook.xlsx"))

    # With DSL commands
    result = processors.excel_to_llm(attach("workbook.xlsx[format:plain][images:false]"))

    # Simple API (auto-detected)
    ctx = Attachments("workbook.xlsx[pages:1-3][tile:2x2]")
    text = str(ctx)
    images = ctx.images

Future improvements:
- Direct Excel-to-image conversion using xlwings or similar
- Better handling of large sheets with automatic scaling
- Support for chart extraction and analysis
- Custom sheet selection and formatting options
- CSV export functionality for individual sheets
"""

from ..core import Attachment
from ..matchers import excel_match
from . import processor


@processor(
    match=excel_match,
    description="Primary Excel processor with sheet summaries and screenshot capabilities",
)
def excel_to_llm(att: Attachment) -> Attachment:
    """
    Process Excel files for LLM consumption.

    Supports DSL commands:
    - format: plain, markdown (default) for different text representations
    - images: true (default), false to control sheet screenshot extraction
    - pages: 1-3,5 for specific sheet selection (treats pages as sheets)
    - resize_images: 50%, 800x600 for image resizing
    - tile: 2x2, 3x1 for sheet tiling

    Text formats:
    - plain: Clean text summary with sheet dimensions and data preview
    - markdown: Structured markdown with sheet headers and table previews (default)

    Future improvements noted in presenter docstrings.
    """

    # Import namespaces properly to get VerbFunction wrappers
    from .. import load, modify, present, refine

    # Determine text format from DSL commands
    format_cmd = att.commands.get("format", "markdown").lower()

    # Handle format aliases
    format_aliases = {
        "text": "plain",
        "txt": "plain",
        "md": "markdown",
        "csv": "csv",
    }
    format_cmd = format_aliases.get(format_cmd, format_cmd)

    # Determine presenters & loaders
    if format_cmd == "plain":
        text_presenter = present.text
        loader_fn = load.excel_to_openpyxl
    elif format_cmd == "csv":
        text_presenter = present.csv
        loader_fn = load.excel_to_libreoffice
    else:  # markdown (default)
        text_presenter = present.markdown
        loader_fn = load.excel_to_openpyxl

    # Determine if images should be included
    include_images = att.commands.get("images", "true").lower() == "true"

    # Build image pipeline if requested
    if include_images and format_cmd != "csv":
        image_pipeline = present.images
    else:
        # Empty pipeline that does nothing
        def image_pipeline(att: Attachment) -> Attachment:  # noqa: D401
            return att

    # Build the complete pipeline
    return (
        att
        | load.url_to_response  # Handle URLs with new morphing architecture
        | modify.morph_to_detected_type  # Smart detection replaces hardcoded url_to_file
        | loader_fn  # <- whichever we chose above
        | modify.pages  # Apply sheet selection if specified
        | text_presenter + image_pipeline + present.metadata
        | refine.tile_images
        | refine.resize_images
        | refine.add_headers
    )
