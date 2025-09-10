"""
PDF to LLM Pipeline Processor
============================

Complete pipeline for processing PDF files optimized for LLM consumption.
Supports clean DSL commands for the Attachments() simple API.

DSL Commands:
    [images:true|false] - Include images (default: true)
    [format:plain|markdown|code] - Text formatting (default: markdown)
        Aliases: text=plain, txt=plain, md=markdown
    [pages:1-5,10] - Specific pages (inherits from existing modify.pages)
    [resize_images:50%|800x600] - Image resize specification (consistent naming)
    [tile:2x2|3x1|4] - Tile multiple PDF pages into grid layout (default: 2x2 for multi-page PDFs)
    [ocr:auto|true|false] - OCR for scanned PDFs (auto=detect and apply if needed)

Note: Multi-page PDFs are automatically tiled in a 2x2 grid by default for better LLM consumption.
Use [tile:false] to disable tiling or [tile:3x1] for custom layouts.

Usage:
    # Explicit processor access
    result = processors.pdf_to_llm(attach("doc.pdf"))

    # With DSL commands
    result = processors.pdf_to_llm(attach("doc.pdf[format:plain][images:false]"))
    result = processors.pdf_to_llm(attach("doc.pdf[format:md]"))  # markdown alias
    result = processors.pdf_to_llm(attach("doc.pdf[images:false]"))  # text only
    result = processors.pdf_to_llm(attach("doc.pdf[tile:2x3][resize_images:400]"))  # tile + resize
    result = processors.pdf_to_llm(attach("doc.pdf[ocr:auto]"))  # auto-OCR for scanned PDFs
    result = processors.pdf_to_llm(attach("doc.pdf[ocr:true]"))  # force OCR

    # Mixing with verbs (power users)
    result = processors.pdf_to_llm(attach("doc.pdf")) | refine.custom_step

    # Like any pipeline and attachment it's ready with adapters
    claude_message_format = result.claude()
"""

from ..core import Attachment
from ..matchers import pdf_match
from . import processor


@processor(match=pdf_match, description="Primary PDF processor with clean DSL commands")
def pdf_to_llm(att: Attachment) -> Attachment:
    """
    Process PDF files for LLM consumption.

    Supports DSL commands (for Attachments() simple API):
    - images: true, false (default: true)
    - format: plain, markdown, code (default: markdown)
      Aliases: text=plain, txt=plain, md=markdown
    - resize_images: 50%, 800x600 (for images)
    - tile: 2x2, 3x1, 4 (for tiling multiple pages)
    - pages: 1-5,10 (for page selection)
    - ocr: auto, true, false (OCR for scanned PDFs, auto=detect and apply if needed)
    """

    # Import namespaces properly to get VerbFunction wrappers
    from .. import load, modify, present, refine

    # Determine text format from DSL commands
    format_cmd = att.commands.get("format", "markdown")

    # Handle format aliases
    format_aliases = {"text": "plain", "txt": "plain", "md": "markdown"}
    format_cmd = format_aliases.get(format_cmd, format_cmd)

    # Build the pipeline based on format
    if format_cmd == "plain":
        text_presenter = present.text
    else:
        # Default to markdown
        text_presenter = present.markdown

    # Determine if images should be included
    include_images = att.commands.get("images", "true").lower() == "true"

    # Build image pipeline if requested
    if include_images:
        image_pipeline = present.images
    else:
        # Empty pipeline that does nothing (avoid lambda for lint rules)
        def image_pipeline(att: Attachment) -> Attachment:  # noqa: D401
            return att

    # Get OCR setting from DSL commands
    ocr_setting = att.commands.get("ocr", "auto").lower()

    if ocr_setting == "true":
        # Force OCR regardless of text extraction quality
        return (
            att
            | load.url_to_response  # Handle URLs with new morphing architecture
            | modify.morph_to_detected_type  # Smart detection replaces hardcoded url_to_file
            | load.pdf_to_pdfplumber
            | modify.pages  # Optional - only acts if [pages:...] present
            # Only run OCR for text (avoid duplicate text from standard presenter)
            | image_pipeline + _perform_inline_ocr + present.metadata
            | refine.tile_images
            | refine.resize_images
        )
    elif ocr_setting == "false":
        # Never use OCR
        return (
            att
            | load.url_to_response  # Handle URLs with new morphing architecture
            | modify.morph_to_detected_type  # Smart detection replaces hardcoded url_to_file
            | load.pdf_to_pdfplumber
            | modify.pages  # Optional - only acts if [pages:...] present
            | text_presenter + image_pipeline + present.metadata  # No OCR
            | refine.tile_images
            | refine.resize_images
        )
    else:
        # Auto mode (default): First extract text, then conditionally add OCR
        # Process with standard pipeline first
        processed = (
            att
            | load.url_to_response  # Handle URLs with new morphing architecture
            | modify.morph_to_detected_type  # Smart detection replaces hardcoded url_to_file
            | load.pdf_to_pdfplumber
            | modify.pages  # Optional - only acts if [pages:...] present
            | text_presenter + image_pipeline + present.metadata  # Standard extraction
            | refine.tile_images
            | refine.resize_images
        )

        # Check if OCR is needed based on text extraction quality
        if processed.metadata.get("is_likely_scanned", False) and processed.metadata.get(
            "text_extraction_quality"
        ) in ["poor", "limited"]:
            # Add OCR for scanned documents (inline)
            processed = processed | _perform_inline_ocr

        return processed


def _perform_inline_ocr(att: Attachment) -> Attachment:
    """Inline OCR extraction using pytesseract/pypdfium2, driven by DSL.

    - Honors `lang` command (e.g., [lang:chi_sim]).
    - Respects `pages` selection via `modify.pages` metadata.
    - Appends an OCR section to `att.text` and updates metadata.
    """
    try:
        import pypdfium2 as pdfium
        import pytesseract
        from PIL import Image  # noqa: F401 - imported for side effects/types
    except ImportError as e:
        att.text += "\n## OCR Text Extraction\n\n"
        att.text += "⚠️ OCR not available: Missing dependencies.\n\n"
        att.text += "Install with:\n"
        att.text += "```bash\n"
        att.text += "pip install pytesseract pypdfium2 pillow\n"
        att.text += "# Ubuntu/Debian (engine + languages)\n"
        att.text += "sudo apt-get install tesseract-ocr\n"
        att.text += "# Example languages: Chinese Simplified\n"
        att.text += "sudo apt-get install tesseract-ocr-chi-sim\n"
        att.text += "# macOS:\n"
        att.text += "brew install tesseract\n"
        att.text += "```\n\n"
        att.text += f"Error: {e}\n\n"
        att.metadata["ocr_error"] = str(e)
        # Log a warning for developers
        try:
            from ..config import verbose_log

            verbose_log(f"OCR unavailable due to missing deps: {e}")
        except Exception:
            pass
        return att

    att.text += "\n## OCR Text Extraction\n\n"

    try:
        # Verify tesseract binary is available
        try:
            import pytesseract

            _ = pytesseract.get_tesseract_version()
        except Exception as e:
            msg = (
                "⚠️ Tesseract engine not found. Please install the tesseract binary.\n\n"
                "Install suggestions:\n\n"
                "- Ubuntu/Debian: sudo apt-get install tesseract-ocr\n"
                "- macOS (Homebrew): brew install tesseract\n"
                "- Windows: Install from https://github.com/tesseract-ocr/tesseract\n\n"
                "You can also set pytesseract.pytesseract.tesseract_cmd to the binary path.\n\n"
            )
            att.text += msg
            att.metadata["ocr_error"] = f"tesseract_not_found: {e}"
            try:
                from ..config import verbose_log

                verbose_log(f"Tesseract not found: {e}")
            except Exception:
                pass
            return att

        # Load bytes for pypdfium2 rendering
        if "temp_pdf_path" in att.metadata:
            with open(att.metadata["temp_pdf_path"], "rb") as f:
                pdf_bytes = f.read()
        elif att.path:
            with open(att.path, "rb") as f:
                pdf_bytes = f.read()
        else:
            att.text += "⚠️ OCR failed: Cannot access PDF file.\n\n"
            return att

        pdf_doc = pdfium.PdfDocument(pdf_bytes)
        num_pages = len(pdf_doc)

        # Page selection (defaults to first 5 for performance)
        if "selected_pages" in att.metadata:
            pages_to_process = att.metadata["selected_pages"]
        else:
            pages_to_process = range(1, min(6, num_pages + 1))
        pages_list = list(pages_to_process)

        # Language selection via DSL (default English)
        ocr_lang = att.commands.get("lang", "eng")

        total_ocr_text = ""
        successful_pages = 0

        for page_num in pages_list:
            if 1 <= page_num <= num_pages:
                try:
                    page = pdf_doc[page_num - 1]
                    pil_image = page.render(scale=2).to_pil()  # upscale for better OCR
                    try:
                        page_text = pytesseract.image_to_string(pil_image, lang=ocr_lang)
                    except pytesseract.TesseractError as te:
                        # Handle missing language data and other tesseract errors gracefully
                        err = str(te)
                        guidance = ""
                        if any(
                            x in err.lower()
                            for x in ["unknown language", "failed loading language", "not found"]
                        ):
                            guidance = (
                                "\n💡 Language data not found. Install traineddata for the requested language.\n\n"
                                "Examples:\n"
                                "- Ubuntu/Debian Chinese (Simplified): sudo apt-get install tesseract-ocr-chi-sim\n"
                                "- Ubuntu/Debian Arabic: sudo apt-get install tesseract-ocr-ara\n"
                                "- macOS: brew install tesseract (includes common languages) or add .traineddata to TESSDATA_PREFIX\n\n"
                            )
                        att.text += (
                            f"### Page {page_num} (OCR)\n\n*['tesseract' error: {err}]*\n"
                            + guidance
                            + "\n"
                        )
                        # Continue to next page
                        continue

                    if page_text.strip():
                        att.text += f"### Page {page_num} (OCR)\n\n{page_text.strip()}\n\n"
                        total_ocr_text += page_text.strip()
                        successful_pages += 1
                    else:
                        att.text += f"### Page {page_num} (OCR)\n\n*[No text detected by OCR]*\n\n"
                except Exception as e:
                    att.text += f"### Page {page_num} (OCR)\n\n*[OCR failed: {str(e)}]*\n\n"

        pdf_doc.close()

        # Summary and metadata
        att.text += "**OCR Summary**:\n"
        att.text += f"- Pages processed: {len(pages_list)}\n"
        att.text += f"- Language: {ocr_lang}\n"
        att.text += f"- Pages with OCR text: {successful_pages}\n"
        att.text += f"- Total OCR text length: {len(total_ocr_text)} characters\n\n"

        att.metadata.update(
            {
                "ocr_performed": True,
                "ocr_pages_processed": len(pages_list),
                "ocr_lang": ocr_lang,
                "ocr_pages_successful": successful_pages,
                "ocr_text_length": len(total_ocr_text),
            }
        )

    except Exception as e:
        att.text += f"⚠️ OCR failed: {str(e)}\n\n"
        att.metadata["ocr_error"] = str(e)
        try:
            from ..config import verbose_log

            verbose_log(f"OCR runtime failure: {e}")
        except Exception:
            pass

    return att
