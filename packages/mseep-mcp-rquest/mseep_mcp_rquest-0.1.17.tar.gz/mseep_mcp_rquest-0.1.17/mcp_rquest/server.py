import json
import os
import tempfile
import threading
import time
import uuid
from typing import Any, Dict, Optional

import anyio
import click
import mcp.types as types
import rnet
import tiktoken
from markdownify import markdownify as md
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from mcp.server.lowlevel import Server
from rnet import HeaderMap

# Import version from package
from mcp_rquest import __version__

# Storage for responses - use system temp directory
RESPONSE_STORAGE_DIR = os.path.join(tempfile.gettempdir(), "mcp-rquest-responses")
os.makedirs(RESPONSE_STORAGE_DIR, exist_ok=True)
response_metadata = {}  # UUID to metadata mapping

# Model loading state
class ModelState:
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"

# Global state for model loading
_MODEL_STATE = {
    "state": ModelState.LOADING,
    "error": None,
    "converter": None,
    "loading_thread": None,
    "start_time": None
}

# Load marker converter in a separate thread
def _load_marker_models():
    try:
        _MODEL_STATE["start_time"] = time.time()
        _MODEL_STATE["state"] = ModelState.LOADING

        # Load the converter
        converter = PdfConverter(artifact_dict=create_model_dict())

        # Update global state
        _MODEL_STATE["converter"] = converter
        _MODEL_STATE["state"] = ModelState.READY
        loading_time = time.time() - _MODEL_STATE["start_time"]
        print(f"PDF models loaded successfully in {loading_time:.2f} seconds")
    except Exception as e:
        # If loading fails, store the error
        _MODEL_STATE["state"] = ModelState.ERROR
        _MODEL_STATE["error"] = str(e)
        print(f"Failed to load PDF models: {e}")

# Start loading models in background thread
def start_model_loading():
    if _MODEL_STATE["loading_thread"] is None or not _MODEL_STATE["loading_thread"].is_alive():
        _MODEL_STATE["loading_thread"] = threading.Thread(target=_load_marker_models, daemon=True)
        _MODEL_STATE["loading_thread"].start()
        print("Started loading PDF models in background thread")

# Get Marker converter instance, returns None if not ready
def get_marker_converter() -> Optional[PdfConverter]:
    # Start loading if not already started
    if _MODEL_STATE["loading_thread"] is None:
        start_model_loading()

    # Return the converter if ready
    if _MODEL_STATE["state"] == ModelState.READY:
        return _MODEL_STATE["converter"]

    # Return None to indicate models aren't ready
    return None

# Check model state
def get_model_state() -> Dict[str, Any]:
    if _MODEL_STATE["state"] == ModelState.LOADING:
        # Calculate loading time if available
        loading_time = None
        if _MODEL_STATE["start_time"] is not None:
            loading_time = time.time() - _MODEL_STATE["start_time"]

        return {
            "state": ModelState.LOADING,
            "message": "PDF models are still loading",
            "loading_time": f"{loading_time:.2f} seconds" if loading_time else "unknown"
        }
    elif _MODEL_STATE["state"] == ModelState.ERROR:
        return {
            "state": ModelState.ERROR,
            "message": "Failed to load PDF models",
            "error": _MODEL_STATE["error"]
        }
    else:
        return {
            "state": ModelState.READY,
            "message": "PDF models are loaded and ready"
        }

def get_content_type(headers: HeaderMap) -> str:
    """
    Get the content type from the headers.
    """
    # Use header_map_to_dict to get the content type
    headers_dict = header_map_to_dict(headers)
    return headers_dict.get("content-type", "unknown")


def store_response(content: str, content_type: str = "unknown") -> Dict[str, Any]:
    """
    Store HTTP response content in a file and return metadata about the stored content.
    """

    response_id = str(uuid.uuid4())
    file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")

    # Store the content to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Check if this might be base64-encoded binary content (PDF)
    is_binary_content = "pdf" in content_type.lower() or "application/pdf" in content_type.lower()

    # Calculate metadata - handle binary content differently
    if is_binary_content:
        # For binary content, we don't meaningfully count lines
        lines = 1
        char_count = len(content)
        # For base64 content, token count calculation is not useful
        token_count = 0
        preview = "Binary PDF content (base64 encoded)"
    else:
        # For text content, calculate normally
        lines = content.count("\n") + 1
        char_count = len(content)
        # Calculate token count using tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's cl100k_base encoding
        token_count = len(encoding.encode(content))
        preview = content[:50] + "..." if len(content) > 50 else content

    # Store metadata
    metadata = {
        "id": response_id,
        "content_type": content_type,
        "size_bytes": len(content.encode("utf-8")),
        "char_count": char_count,
        "line_count": lines,
        "token_count": token_count,  # Add token count to metadata
        "preview": preview,
        "tips": " ".join([
            "Response content is large and may consume many tokens.",
            "Consider using get_stored_response_with_markdown to retrieve the full content in markdown format.",
        ])
        if "html" in content_type.lower() or "pdf" in content_type.lower() or "application/pdf" in content_type.lower()
        else " ".join([
            "Response content is large and may consume many tokens.",
            "Consider asking the user for permission before retrieving the full content.",
            "You can use get_stored_response with start_line and end_line parameters to retrieve only a portion of the content.",
        ]),
    }
    response_metadata[response_id] = metadata

    return metadata


def should_store_content(content: str, force_store: bool = False) -> bool:
    """
    Determine if content should be stored based on token count or force flag.
    Returns True if content token count > 500 tokens or force_store is True.
    Using tiktoken for accurate AI token estimation.
    """
    if force_store:
        return True

    # Use tiktoken to count tokens accurately
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding for newer models
        token_count = len(encoding.encode(content))
        return token_count > 500  # Threshold of 500 tokens (approx. 375-750 words)
    except Exception:
        # Fallback to character count if tiktoken fails
        return len(content) > 2000

def header_map_to_dict(headers: HeaderMap) -> dict:
    """
    Convert HeaderMap to a dictionary using items() iterator.
    """
    result = {}
    for key, value in headers.items():
        # Convert keys and values to strings
        str_key = key.decode('utf-8') if isinstance(key, bytes) else str(key)
        str_value = value.decode('utf-8') if isinstance(value, bytes) else value
        result[str_key] = str_value
    return result

def cookies_to_dict(cookies) -> dict:
    """
    Convert cookies to a serializable dictionary format.
    """
    if not cookies:
        return {}

    # Handle different cookie object types
    if hasattr(cookies, "items"):
        # If it's a dict-like object, convert it to a dict
        return dict(cookies.items())
    elif hasattr(cookies, "__iter__"):
        # If it's an iterable, convert to a dict using key/value pairs
        cookie_dict = {}
        for cookie in cookies:
            if hasattr(cookie, "key") and hasattr(cookie, "value"):
                cookie_dict[str(cookie.key)] = str(cookie.value)
            elif isinstance(cookie, tuple) and len(cookie) >= 2:
                cookie_dict[str(cookie[0])] = str(cookie[1])
        return cookie_dict
    else:
        # If we can't handle the cookie object, return an empty dict
        return {}

async def perform_http_request(
    method: str,
    url: str,
    proxy: str = None,
    headers: dict = None,
    cookies: dict = None,
    allow_redirects: bool = True,
    max_redirects: int = 10,
    auth: str = None,
    bearer_auth: str = None,
    basic_auth: tuple[str, str] = None,
    query: list[tuple[str, str]] = None,
    form: list[tuple[str, str]] = None,
    json_payload: dict = None,
    body: dict = None,
    multipart: list[tuple[str, str]] = None,
    force_store_response_content: bool = False,
) -> Dict[str, Any]:
    """
    Common implementation for HTTP requests.
    """

    # Handle authentication
    kwds = {}
    if proxy:
        kwds["proxy"] = proxy
    if headers:
        kwds["headers"] = headers
    if cookies:
        kwds["cookies"] = cookies
    if allow_redirects:
        kwds["allow_redirects"] = allow_redirects
    if max_redirects:
        kwds["max_redirects"] = max_redirects
    if auth:
        kwds["auth"] = auth
    if bearer_auth:
        kwds["bearer_auth"] = bearer_auth
    if basic_auth:
        # Convert basic_auth list to tuple if needed
        kwds["basic_auth"] = tuple(basic_auth)
    if query:
        # Convert list of lists to list of tuples if needed
        kwds["query"] = [tuple(q) for q in query]
    if form:
        # Convert list of lists to list of tuples if needed
        kwds["form"] = [tuple(f) for f in form]
    if json_payload:
        kwds["json"] = json_payload
    if body:
        kwds["body"] = body
    if multipart:
        # Convert list of lists to list of tuples if needed
        kwds["multipart"] = [tuple(m) for m in multipart]

    resp = await getattr(rnet.Client(), method.lower())(url, **kwds)
    content_type = get_content_type(resp.headers)

    # Handle different content types
    if "application/json" in content_type:
        content = await resp.json()
    elif "application/pdf" in content_type or content_type.endswith("pdf"):
        # For PDF content, store as binary and convert to base64
        import base64
        # Use resp.bytes() to get binary content
        content_bytes = await resp.bytes()
        content = base64.b64encode(content_bytes).decode('utf-8')
    else:
        content = await resp.text()

    # Prepare response data
    response_data = {
        "status": resp.status,
        "status_code": str(resp.status_code),
        "headers": header_map_to_dict(resp.headers),
        "cookies": cookies_to_dict(resp.cookies),
        "url": resp.url,
    }

    # Store content if needed based on length or force flag
    if should_store_content(content, force_store_response_content):
        metadata = store_response(content, content_type)
        response_data["response_content"] = metadata
    else:
        response_data["content"] = content

    return [types.TextContent(type="text", text=json.dumps(response_data, ensure_ascii=False))]

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.version_option(version=__version__, prog_name="mcp-rquest")
def main(port: int, transport: str) -> int:
    # Start loading models in background
    start_model_loading()

    app = Server("mcp-rquest")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls"""

        if name == "http_get":
            return await perform_http_request("GET", **arguments)
        elif name == "http_post":
            return await perform_http_request("POST", **arguments)
        elif name == "http_put":
            return await perform_http_request("PUT", **arguments)
        elif name == "http_delete":
            return await perform_http_request("DELETE", **arguments)
        elif name == "http_patch":
            return await perform_http_request("PATCH", **arguments)
        elif name == "http_head":
            return await perform_http_request("HEAD", **arguments)
        elif name == "http_options":
            return await perform_http_request("OPTIONS", **arguments)
        elif name == "http_trace":
            return await perform_http_request("TRACE", **arguments)
        elif name == "get_stored_response":
            response_id = arguments.get("response_id")
            start_line = arguments.get("start_line")
            end_line = arguments.get("end_line")

            if response_id not in response_metadata:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Response with ID {response_id} not found"}))]

            metadata = response_metadata[response_id]
            file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if start_line is not None and end_line is not None:
                    # Convert to 0-based indexing
                    start_line = max(1, start_line) - 1
                    end_line = min(metadata["line_count"], end_line)

                    # Extract the specified lines
                    lines = content.splitlines()
                    if start_line < len(lines) and end_line >= start_line:
                        partial_content = "\n".join(lines[start_line:end_line])
                        result = {
                            **metadata,
                            "content": partial_content,
                            "is_partial": True,
                            "start_line": start_line + 1,
                            "end_line": end_line,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

                # Return full content
                result = {**metadata, "content": content, "is_partial": False}
                return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Failed to retrieve response: {str(e)}"}, ensure_ascii=False))]
        elif name == "get_stored_response_with_markdown":
            response_id = arguments.get("response_id")

            if response_id not in response_metadata:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Response with ID {response_id} not found"}))]

            metadata = response_metadata[response_id]
            file_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.txt")
            content_type = metadata["content_type"]

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Convert HTML to Markdown if applicable
                if "html" in content_type.lower():
                    try:
                        markdown_content = md(content)
                        result = {
                            **metadata,
                            "content": markdown_content,
                            "is_markdown": True,
                            "original_content_type": content_type,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                    except Exception as e:
                        result = {
                            "error": f"Failed to convert HTML to Markdown: {str(e)}",
                            "content": content,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                # Add PDF handling using marker library
                elif "pdf" in content_type.lower():
                    try:
                        # Check if models are ready
                        converter = get_marker_converter()
                        if converter is None:
                            model_state = get_model_state()
                            return [types.TextContent(type="text", text=json.dumps({
                                "error": f"Models not ready yet. Current state: {model_state['state']}",
                                "model_state": model_state,
                                "message": "Please try again later when the models are loaded."
                            }, ensure_ascii=False))]

                        # Create a temporary PDF file
                        temp_pdf_path = os.path.join(RESPONSE_STORAGE_DIR, f"{response_id}.pdf")

                        try:
                            # First, try to decode as base64
                            import base64
                            pdf_content = base64.b64decode(content)
                            # Write binary content to file
                            with open(temp_pdf_path, "wb") as pdf_file:
                                pdf_file.write(pdf_content)
                        except Exception as decode_err:
                            # If base64 decoding fails, try writing the content directly
                            try:
                                # If it's already binary or text, write accordingly
                                if isinstance(content, bytes):
                                    with open(temp_pdf_path, "wb") as pdf_file:
                                        pdf_file.write(content)
                                else:
                                    with open(temp_pdf_path, "w", encoding="utf-8") as pdf_file:
                                        pdf_file.write(content)
                            except Exception as write_err:
                                return [types.TextContent(type="text", text=json.dumps({
                                    "error": f"Failed to write PDF content: Base64 decode error: {str(decode_err)}, Write error: {str(write_err)}",
                                    "content": content[:100] + "..." if len(content) > 100 else content
                                }, ensure_ascii=False))]

                        # Convert PDF to Markdown using marker
                        rendered = converter(temp_pdf_path)
                        markdown_content, _, _ = text_from_rendered(rendered)

                        # Clean up temporary file
                        try:
                            os.remove(temp_pdf_path)
                        except:
                            pass

                        result = {
                            **metadata,
                            "content": markdown_content,
                            "is_markdown": True,
                            "original_content_type": content_type,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                    except Exception as e:
                        result = {
                            "error": f"Failed to convert PDF to Markdown: {str(e)}",
                            "content": content[:100] + "..." if len(content) > 100 else content,
                        }
                        return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
                else:
                    # Non-supported content type
                    return [types.TextContent(type="text", text=json.dumps({"error": f"Content type {content_type} is not supported for markdown conversion. Only HTML and PDF are supported."}))]
            except Exception as e:
                return [types.TextContent(type="text", text=json.dumps({"error": f"Failed to retrieve response: {str(e)}"}, ensure_ascii=False))]
        elif name == "get_model_state":
            # Return current model loading state
            return [types.TextContent(type="text", text=json.dumps(get_model_state(), ensure_ascii=False))]
        elif name == "restart_model_loading":
            # Force restart model loading
            start_model_loading()
            return [types.TextContent(type="text", text=json.dumps({"message": "Model loading restarted"}, ensure_ascii=False))]
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """List available tools"""
        tools = [
            # HTTP tools
            types.Tool(
                name="http_get",
                description="Make an HTTP GET request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_post",
                description="Make an HTTP POST request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_put",
                description="Make an HTTP PUT request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_delete",
                description="Make an HTTP DELETE request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_patch",
                description="Make an HTTP PATCH request to the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "form": {"type": "array", "description": "Form data as [[key, value], ...]"},
                        "json_payload": {"type": "object", "description": "JSON payload"},
                        "body": {"type": "object", "description": "Request body"},
                        "multipart": {"type": "array", "description": "Multipart data as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_head",
                description="Make an HTTP HEAD request to retrieve only headers from the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_options",
                description="Make an HTTP OPTIONS request to retrieve options for the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            types.Tool(
                name="http_trace",
                description="Make an HTTP TRACE request for diagnostic tracing of the specified URL",
                inputSchema={
                    "type": "object",
                    "required": ["url"],
                    "properties": {
                        "url": {"type": "string", "description": "URL to send the request to"},
                        "proxy": {"type": "string", "description": "Proxy to use for the request"},
                        "headers": {"type": "object", "description": "Headers to include in the request"},
                        "cookies": {"type": "object", "description": "Cookies to include in the request"},
                        "allow_redirects": {"type": "boolean", "description": "Whether to follow redirects"},
                        "max_redirects": {"type": "integer", "description": "Maximum number of redirects to follow"},
                        "auth": {"type": "string", "description": "Authentication credentials"},
                        "bearer_auth": {"type": "string", "description": "Bearer token for authentication"},
                        "basic_auth": {"type": "array", "description": "Basic auth credentials as [username, password]"},
                        "query": {"type": "array", "description": "Query parameters as [[key, value], ...]"},
                        "force_store_response_content": {"type": "boolean", "description": "Force storing response content regardless of size"},
                    }
                }
            ),
            # HTTP Response tools
            types.Tool(
                name="get_stored_response",
                description="Retrieve a stored HTTP response by its ID",
                inputSchema={
                    "type": "object",
                    "required": ["response_id"],
                    "properties": {
                        "response_id": {"type": "string", "description": "ID of the stored response"},
                        "start_line": {"type": "integer", "description": "Starting line number (1-indexed)"},
                        "end_line": {"type": "integer", "description": "Ending line number (inclusive)"},
                    }
                }
            ),
            types.Tool(
                name="get_stored_response_with_markdown",
                description="Retrieve a stored HTTP response by its ID and convert it to Markdown format. Supports HTML and PDF content types. (Converting large PDF to Markdown may cause timeout, just wait and try again.)",
                inputSchema={
                    "type": "object",
                    "required": ["response_id"],
                    "properties": {
                        "response_id": {"type": "string", "description": "ID of the stored response"},
                    }
                }
            ),
            # PDF Model-related tools
            types.Tool(
                name="get_model_state",
                description="Get the current state of the PDF models(used by `get_stored_response_with_markdown`) loading process",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="restart_model_loading",
                description="Restart the PDF models(used by `get_stored_response_with_markdown`) loading process if it failed or got stuck",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
        ]
        return tools

    # Setup server based on transport type
    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn
        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        from mcp.server.stdio import stdio_server

        async def arun():
            async with stdio_server() as streams:
                await app.run(
                    streams[0], streams[1], app.create_initialization_options()
                )

        anyio.run(arun)

    return 0
