from typing import Any

from .core import Attachment, AttachmentCollection, adapter

# --- ADAPTERS ---

# TODO: Implement additional adapters for popular LLM providers and frameworks
# Priority adapters from roadmap:
# - bedrock() - AWS Bedrock API format
# - azure_openai() - Azure OpenAI API format
# - ollama() - Ollama local model API format
# - litellm() - LiteLLM universal adapter format
# - langchain() - LangChain message format
# - openrouter() - OpenRouter API format
# Each adapter should follow the same pattern as existing ones:
# 1. Handle both Attachment and AttachmentCollection inputs
# 2. Use _handle_collection() helper for collections
# 3. Format text and images according to target API specification
# 4. Include proper error handling for missing dependencies
# 5. Add comprehensive docstrings with usage examples


def _handle_collection(input_obj: Attachment | AttachmentCollection) -> Attachment:
    """Convert AttachmentCollection to single Attachment for adapter processing."""
    if isinstance(input_obj, AttachmentCollection):
        return input_obj.to_attachment()
    return input_obj


@adapter
def openai_chat(
    input_obj: Attachment | AttachmentCollection, prompt: str = ""
) -> list[dict[str, Any]]:
    """Adapt for OpenAI chat completion API."""
    att = _handle_collection(input_obj)

    content = []
    if prompt:
        content.append({"type": "text", "text": prompt})

    if att.text:
        content.append({"type": "text", "text": att.text})

    for img in att.images:
        if img and isinstance(img, str) and len(img) > 10:  # Basic validation
            # Check if it's already a data URL
            if img.startswith("data:image/"):
                content.append({"type": "image_url", "image_url": {"url": img}})
            elif not img.endswith("_placeholder"):
                # It's raw base64, add the data URL prefix
                content.append(
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
                )

    return [{"role": "user", "content": content}]


@adapter
def openai_responses(
    input_obj: Attachment | AttachmentCollection, prompt: str = ""
) -> list[dict[str, Any]]:
    """Adapt for OpenAI Responses API (different format from chat completions)."""
    att = _handle_collection(input_obj)

    content = []
    if prompt:
        content.append({"type": "input_text", "text": prompt})

    if att.text:
        content.append({"type": "input_text", "text": att.text})

    for img in att.images:
        if img and isinstance(img, str) and len(img) > 10:  # Basic validation
            # Check if it's already a data URL
            if img.startswith("data:image/"):
                content.append(
                    {"type": "input_image", "image_url": img}  # Direct string, not nested
                )
            elif not img.endswith("_placeholder"):
                # It's raw base64, add the data URL prefix
                content.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{img}",  # Direct string
                    }
                )

    return [{"role": "user", "content": content}]


@adapter
def claude(input_obj: Attachment | AttachmentCollection, prompt: str = "") -> list[dict[str, Any]]:
    """Adapt for Claude API."""
    att = _handle_collection(input_obj)

    content = []

    # Check for prompt in commands (from DSL)
    dsl_prompt = att.commands.get("prompt", "")

    # Combine prompts: parameter prompt takes precedence, DSL prompt as fallback
    effective_prompt = prompt or dsl_prompt

    if effective_prompt and att.text:
        content.append({"type": "text", "text": f"{effective_prompt}\n\n{att.text}"})
    elif effective_prompt:
        content.append({"type": "text", "text": effective_prompt})
    elif att.text:
        content.append({"type": "text", "text": att.text})

    for img in att.images:
        if img and isinstance(img, str) and len(img) > 10:  # Basic validation
            # Extract base64 data for Claude
            base64_data = img
            if img.startswith("data:image/"):
                # Extract just the base64 part after the comma
                if "," in img:
                    base64_data = img.split(",", 1)[1]
                else:
                    continue  # Skip malformed data URLs
            elif img.endswith("_placeholder"):
                continue  # Skip placeholder images

            content.append(
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": base64_data},
                }
            )

    return [{"role": "user", "content": content}]


@adapter
def openai(input_obj: Attachment | AttachmentCollection, prompt: str = "") -> list[dict[str, Any]]:
    """Alias for openai_chat - backwards compatibility with simple API."""
    return openai_chat(input_obj, prompt)


@adapter
def dspy(input_obj: Attachment | AttachmentCollection) -> "DSPyAttachment":
    """Adapt Attachment for DSPy signatures as a BaseType-compatible object."""
    att = _handle_collection(input_obj)

    try:
        # Try to import DSPy and Pydantic
        import dspy
        import pydantic

        # Try to import the new BaseType from DSPy 2.6.25+
        try:
            from dspy.adapters.types import BaseType

            use_new_basetype = True
        except ImportError:
            # Fallback for older DSPy versions
            use_new_basetype = False

        if use_new_basetype:
            # DSPy 2.6.25+ with new BaseType
            class DSPyAttachment(BaseType):
                """DSPy-compatible wrapper for Attachment objects following new BaseType pattern."""

                # Store the attachment data
                text: str = ""
                images: list[str] = []
                audio: list[str] = []
                path: str = ""
                metadata: dict[str, Any] = {}

                # Use new ConfigDict format for Pydantic v2
                model_config = pydantic.ConfigDict(
                    frozen=True,
                    str_strip_whitespace=True,
                    validate_assignment=True,
                    extra="forbid",
                )

                def format(self) -> list[dict[str, Any]]:
                    """Format for DSPy 2.6.25+ - returns list of content dictionaries."""
                    content_parts = []

                    if self.text:
                        content_parts.append({"type": "text", "text": self.text})

                    if self.images:
                        # Process images - ensure they're properly formatted
                        for img in self.images:
                            if img and isinstance(img, str) and len(img) > 10:
                                # Check if it's already a data URL
                                if img.startswith("data:image/"):
                                    content_parts.append(
                                        {"type": "image_url", "image_url": {"url": img}}
                                    )
                                elif not img.endswith("_placeholder"):
                                    # It's raw base64, add the data URL prefix
                                    content_parts.append(
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/png;base64,{img}"},
                                        }
                                    )

                    return (
                        content_parts
                        if content_parts
                        else [{"type": "text", "text": f"Attachment: {self.path}"}]
                    )

                def __str__(self):
                    # For normal usage, just return the text content
                    return self.text if self.text else f"Attachment: {self.path}"

                def __repr__(self):
                    if self.text:
                        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
                        return f"DSPyAttachment(text='{text_preview}', images={len(self.images)})"
                    elif self.images:
                        return f"DSPyAttachment(images={len(self.images)}, path='{self.path}')"
                    else:
                        return f"DSPyAttachment(path='{self.path}')"

        elif hasattr(pydantic, "ConfigDict"):
            # Legacy DSPy with Pydantic v2
            from pydantic import ConfigDict

            class DSPyAttachment(pydantic.BaseModel):
                """DSPy-compatible wrapper for Attachment objects following Image pattern."""

                # Store the attachment data
                text: str = ""
                images: list[str] = []
                audio: list[str] = []
                path: str = ""
                metadata: dict[str, Any] = {}

                # Use new ConfigDict format for Pydantic v2
                model_config = ConfigDict(
                    frozen=True,
                    str_strip_whitespace=True,
                    validate_assignment=True,
                    extra="forbid",
                )

                @pydantic.model_serializer
                def serialize_model(self):
                    """Serialize for DSPy compatibility - following Image pattern."""
                    # Create a comprehensive representation that includes both text and images
                    content_parts = []

                    if self.text:
                        content_parts.append(f"<DSPY_TEXT_START>{self.text}<DSPY_TEXT_END>")

                    if self.images:
                        # Process images - ensure they're properly formatted
                        valid_images = []
                        for img in self.images:
                            if img and isinstance(img, str):
                                # Check if it's already a data URL
                                if img.startswith("data:image/"):
                                    valid_images.append(img)
                                elif img and not img.endswith("_placeholder"):
                                    # It's raw base64, add the data URL prefix
                                    valid_images.append(f"data:image/png;base64,{img}")

                        if valid_images:
                            image_tags = ""
                            for img in valid_images:
                                image_tags += f"<DSPY_IMAGE_START>{img}<DSPY_IMAGE_END>"
                            content_parts.append(image_tags)

                    if content_parts:
                        return "".join(content_parts)
                    else:
                        return (
                            f"<DSPY_ATTACHMENT_START>Attachment: {self.path}<DSPY_ATTACHMENT_END>"
                        )

                def __str__(self):
                    return self.serialize_model()

                def __repr__(self):
                    if self.text:
                        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
                        return f"DSPyAttachment(text='{text_preview}', images={len(self.images)})"
                    elif self.images:
                        return f"DSPyAttachment(images={len(self.images)}, path='{self.path}')"
                    else:
                        return f"DSPyAttachment(path='{self.path}')"

        else:
            # Fallback for older Pydantic versions
            class DSPyAttachment(pydantic.BaseModel):
                """DSPy-compatible wrapper for Attachment objects (legacy Pydantic)."""

                text: str = ""
                images: list[str] = []
                audio: list[str] = []
                path: str = ""
                metadata: dict[str, Any] = {}

                class Config:
                    frozen = True
                    str_strip_whitespace = True
                    validate_assignment = True
                    extra = "forbid"

                def serialize_model(self):
                    """Simple serialization for older Pydantic."""
                    if self.text:
                        return self.text
                    elif self.images:
                        return f"Attachment with {len(self.images)} images"
                    else:
                        return f"Attachment: {self.path}"

                def __str__(self):
                    return self.serialize_model()

        # Clean up the images list - remove any invalid entries
        clean_images = []
        for img in att.images:
            if img and isinstance(img, str) and len(img) > 10:  # Basic validation
                # If it's already a data URL, keep it as is
                if img.startswith("data:image/"):
                    clean_images.append(img)
                # If it's raw base64, we'll handle it in the serializer
                elif not img.endswith("_placeholder"):
                    clean_images.append(img)

        # Create and return the DSPy-compatible object
        return DSPyAttachment(
            text=att.text,
            images=clean_images,
            audio=att.audio,
            path=att.path,
            metadata=att.metadata,
        )

    except ImportError as e:
        # Better error handling when DSPy/Pydantic is not available
        missing_packages = []

        try:
            import dspy
        except ImportError:
            missing_packages.append("dspy-ai")

        try:
            import pydantic
        except ImportError:
            missing_packages.append("pydantic")

        if missing_packages:
            error_msg = (
                f"DSPy adapter requires {' and '.join(missing_packages)} to be installed.\n\n"
                f"Install with:\n"
                f"  pip install {' '.join(missing_packages)}\n"
                f"  # or\n"
                f"  uv add {' '.join(missing_packages)}\n\n"
                f"If you don't need DSPy integration, use other adapters like:\n"
                f"  attachment.openai_chat()  # For OpenAI\n"
                f"  attachment.claude()       # For Claude"
            )
        else:
            error_msg = f"DSPy adapter failed: {e}"

        raise ImportError(error_msg) from e


@adapter
def agno(input_obj: Attachment | AttachmentCollection, prompt: str = "") -> dict[str, Any]:
    """Adapt for agno Agent.run() method."""
    att = _handle_collection(input_obj)

    try:
        from agno.media import Image as AgnoImage
    except ImportError as e:
        raise ImportError(
            "agno adapter requires agno to be installed.\n\n"
            "Install with:\n"
            "  pip install agno\n"
            "  # or\n"
            "  uv add agno\n\n"
            "If you don't need agno integration, use other adapters like:\n"
            "  attachment.openai_chat()  # For OpenAI\n"
            "  attachment.claude()       # For Claude"
        ) from e

    # Handle prompt - check DSL commands first, then parameter
    dsl_prompt = att.commands.get("prompt", "")
    effective_prompt = prompt or dsl_prompt

    # Combine prompt and text content
    message_parts = []
    if effective_prompt:
        message_parts.append(effective_prompt)
    if att.text:
        message_parts.append(att.text)

    result = {
        "message": " ".join(message_parts) if message_parts else "",
        "images": [
            AgnoImage(url=img) for img in att.images if img and not img.endswith("_placeholder")
        ],
    }

    return result


@adapter
def to_clipboard_text(input_obj: Attachment | AttachmentCollection, prompt: str = "") -> None:
    """Copy the text content of the attachment(s) to the clipboard, optionally with a prompt."""
    att = _handle_collection(input_obj)

    try:
        import copykitten

        # Handle prompt - check DSL commands first, then parameter
        dsl_prompt = att.commands.get("prompt", "")
        effective_prompt = prompt or dsl_prompt

        # Combine prompt and text content
        content_parts = []
        if effective_prompt:
            content_parts.append(effective_prompt)
        if att.text:
            content_parts.append(att.text)

        final_content = "\n\n".join(content_parts) if content_parts else ""

        copykitten.copy(final_content)

        if effective_prompt:
            print(f"📋 Text with prompt (length: {len(final_content)}) copied to clipboard.")
        else:
            print(f"📋 Text (length: {len(final_content)}) copied to clipboard.")

    except ImportError as err:
        raise ImportError(
            "Clipboard adapters require 'copykitten' to be installed.\n\n"
            "Install with:\n"
            "  pip install copykitten\n"
            "  # or\n"
            "  uv add copykitten"
        ) from err
    except Exception as e:
        print(f"⚠️ Could not copy text to clipboard: {e}")


@adapter
def to_clipboard_image(input_obj: Attachment | AttachmentCollection) -> None:
    """Copy the first image of the attachment(s) to the clipboard."""
    att = _handle_collection(input_obj)

    if not att.images:
        print("⚠️ No images found to copy.")
        return

    try:
        import base64
        import io

        import copykitten
        from PIL import Image

        # Get the first image (it's a base64 data URL)
        img_b64 = att.images[0]

        if img_b64.startswith("data:image/"):
            img_data_b64 = img_b64.split(",", 1)[1]
        else:
            img_data_b64 = img_b64

        img_data = base64.b64decode(img_data_b64)
        img = Image.open(io.BytesIO(img_data))

        # copykitten expects RGBA format
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Get raw pixel data
        pixels = img.tobytes()

        copykitten.copy_image(pixels, img.width, img.height)
        print(f"📋 Image ({img.width}x{img.height}) copied to clipboard.")

    except ImportError as err:
        raise ImportError(
            "Clipboard adapters require 'copykitten' and 'Pillow' to be installed.\n\n"
            "Install with:\n"
            "  pip install copykitten Pillow\n"
            "  # or\n"
            "  uv add copykitten Pillow"
        ) from err
    except Exception as e:
        print(f"⚠️ Could not copy image to clipboard: {e}")
