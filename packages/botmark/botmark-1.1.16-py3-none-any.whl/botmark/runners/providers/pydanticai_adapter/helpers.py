import mimetypes, os, base64, textwrap
from typing import Any, Mapping, Union
from ....utils.helpers import decode_data_url

from pydantic_ai import ImageUrl, BinaryContent, DocumentUrl
from pydantic_ai.tools import Tool
from pydantic_ai.toolsets import FunctionToolset, CombinedToolset

def get_toolset( tools ):

    def create_toolset_from_code(code, shared_context={}, attributes= {}, max_retries = 1):
        tools = []
        local_namespace = {}
        exec(textwrap.dedent(code), shared_context, local_namespace)
        for name, obj in local_namespace.items():
            if callable(obj):
                tools.append(
                    Tool(
                        obj,
                        name=name,
                        description=obj.__doc__ or "No description."
                    )
                )
        return FunctionToolset( tools = tools, max_retries = max_retries )

    tool_sets = []
    for t in tools:
        tool_sets.append( create_toolset_from_code ( **t) )

    return [ CombinedToolset ( tool_sets ) ]

def resolve_image_url(image_url: str) -> ImageUrl:

    if not image_url:
        raise ValueError("No image path or URL provided.")

    # Already a URL or data:-URL
    if image_url.startswith(("http://", "https://", "data:")):
        return ImageUrl(url=image_url)

    # Local file → convert to base64 data URL
    if os.path.isfile(image_url):
        try:
            with open(image_url, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode("utf-8")

            mime_type, _ = mimetypes.guess_type(image_url)
            if mime_type is None:
                mime_type = "image/png"  # fallback

            return ImageUrl(url=f"data:{mime_type};base64,{encoded}")
        except Exception as e:
            print(f"Error processing the image file: {e}")
            return ImageUrl(url=image_url)

    # Fallback for unknown string
    return ImageUrl(url=image_url)

def resolve_link( href ) -> Any:

    # 1. Data-URL
    if href.startswith("data:"):
        try:
            mime_type, link_bytes = decode_data_url(href)
            return BinaryContent(data=link_bytes, media_type=mime_type)
        except Exception as e:
            print(f"Error decoding data URL: {e}")

    # 2. local file
    elif os.path.isfile(href):
        try:
            mime_type, _ = mimetypes.guess_type(href)
            link_bytes = open(href, "rb").read()
            return BinaryContent(data=link_bytes, media_type=mime_type or "application/octet-stream")
        except Exception as e:
            print(f"Error processing the local file: {e}")
    
    # 3. HTTP/HTTPS-URL
    elif href.startswith("http://") or href.startswith("https://"):
        try:
            return DocumentUrl ( url=href)
        except Exception as e:
            print(f"Error fetching URL: {e}")
