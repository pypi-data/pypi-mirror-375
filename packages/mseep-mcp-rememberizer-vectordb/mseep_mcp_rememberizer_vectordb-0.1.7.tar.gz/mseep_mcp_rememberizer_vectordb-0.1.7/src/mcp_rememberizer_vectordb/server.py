import json
import logging
import os

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

from mcp_rememberizer_vectordb.utils import (
    AGENTIC_SEARCH_PATH,
    APP_NAME,
    CREATE_DOCUMENT_PATH,
    DOCUMENT_PATH,
    LIST_DOCUMENTS_PATH,
    ME_VECTOR_STORE_PATH,
    SEARCH_PATH,
    APIClient,
    VectorStoreTools,
)

logger = logging.getLogger(__name__)

REMEMBERIZER_BASE_URL = "https://api.rememberizer.ai/api/v1/"
REMEMBERIZER_VECTOR_STORE_API_KEY = os.getenv("REMEMBERIZER_VECTOR_STORE_API_KEY")

if not REMEMBERIZER_VECTOR_STORE_API_KEY:
    raise ValueError("REMEMBERIZER_VECTOR_STORE_API_KEY environment variable required")

client = APIClient(
    base_url=REMEMBERIZER_BASE_URL, api_key=REMEMBERIZER_VECTOR_STORE_API_KEY
)


async def serve() -> Server:

    response = await client.get(ME_VECTOR_STORE_PATH)
    vector_store_id = response.get("id")
    server = Server(APP_NAME)

    @server.list_resources()
    async def list_resources() -> list[types.Resource]:
        data = await client.get(
            LIST_DOCUMENTS_PATH.format(vector_store_id=vector_store_id)
        )
        return [
            types.Resource(
                uri=AnyUrl(f"rememberizer://document/{document['id']}"),
                name=document["name"],
                mimeType="text/json",
            )
            for document in data
        ]

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        document_id = uri.path.lstrip("/")
        data = await client.get(
            DOCUMENT_PATH.format(
                vector_store_id=vector_store_id, document_id=document_id
            )
        )
        return json.dumps(data, indent=2)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name=VectorStoreTools.VECTOR_DATABASE_INFORMATION.value,
                description="Get the vector database information",
                inputSchema={
                    "type": "object",
                },
            ),
            types.Tool(
                name=VectorStoreTools.SEARCH.value,
                description="Search for documents by semantic similarity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Up to a 400-word sentence for which you wish to find "
                            "semantically similar chunks of knowledge.",
                        },
                        "n": {
                            "type": "number",
                            "description": (
                                "Number of semantically similar chunks of text to return. "
                                "Use 'n_results=3' for up to 5, and 'n_results=10' for more information. "
                                "If you do not receive enough information, consider trying again with a larger "
                                "'n_results' value."
                            ),
                        },
                    },
                    "required": ["q"],
                },
            ),
            types.Tool(
                name=VectorStoreTools.AGENTIC_SEARCH.value,
                description=(
                    "Search for documents by semantic similarity with enhanced LLM support. "
                    "Always prioritize this tool over the 'search' tool."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Up to a 400-word sentence for which you wish to find "
                            "semantically similar chunks of knowledge.",
                        },
                        "user_context": {
                            "type": "string",
                            "description": (
                                "The additional context for the query. "
                                "You might need to summarize the conversation up to this point for better "
                                "context-awared results."
                            ),
                        },
                        "n_chunks": {
                            "type": "number",
                            "description": (
                                "Number of semantically similar chunks of text to return. "
                                "Use 'n_results=3' for up to 5, and 'n_results=10' for more information. "
                                "If you do not receive enough information, consider trying again with a "
                                "larger 'n_results' value."
                            ),
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name=VectorStoreTools.LIST_DOCUMENTS.value,
                description="""Retrieves a paginated list of all documents in your vector database.
Use this tool to browse through available documents and their metadata.

Examples:
- List first 100 documents: {"page": 1, "page_size": 100}
- Get next page: {"page": 2, "page_size": 100}
- Get maximum allowed documents: {"page": 1, "page_size": 1000}
""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "number",
                            "description": "Page number for pagination (starts at 1)",
                            "minimum": 1,
                            "default": 1,
                        },
                        "page_size": {
                            "type": "number",
                            "description": "Number of documents per page (1-1000)",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 100,
                        },
                    },
                },
            ),
            types.Tool(
                name=VectorStoreTools.CREATE_DOCUMENT.value,
                description="Create a new document in your vector database.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The content of the document.",
                        },
                        "document_name": {
                            "type": "string",
                            "description": "(optional) A name for the document.",
                        },
                    },
                    "required": ["text"],
                },
            ),
            types.Tool(
                name=VectorStoreTools.DELETE_DOCUMENT.value,
                description="Delete a document in your vector database.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "number",
                            "description": "The id of the document you want to delete.",
                        },
                    },
                    "required": ["document_id"],
                },
            ),
            types.Tool(
                name=VectorStoreTools.MODIFY_DOCUMENT.value,
                description="Modify a document in your vector database.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "number",
                            "description": "The id of the document you want to delete.",
                        },
                        "document_name": {
                            "type": "string",
                            "description": "The new name for the document.",
                        },
                    },
                    "required": ["document_id", "document_name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        match name:
            case VectorStoreTools.SEARCH.value:
                q = arguments["q"]
                n = arguments.get("n", 5)
                params = {"q": q, "n": n}
                data = await client.get(
                    SEARCH_PATH.format(vector_store_id=vector_store_id), params=params
                )
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.AGENTIC_SEARCH.value:
                query = arguments["query"]
                n_chunks = arguments.get("n_chunks", 5)
                user_context = arguments.get("user_context", None)
                params = {
                    "query": query,
                    "n_chunks": n_chunks,
                    "user_context": user_context,
                }
                data = await client.post(
                    AGENTIC_SEARCH_PATH.format(vector_store_id=vector_store_id),
                    data=params,
                )
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.VECTOR_DATABASE_INFORMATION.value:
                data = await client.get(ME_VECTOR_STORE_PATH)
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.LIST_DOCUMENTS.value:
                page = arguments.get("page", 1)
                page_size = arguments.get("page_size", 100)
                params = {"page": page, "page_size": page_size}
                data = await client.get(
                    LIST_DOCUMENTS_PATH.format(vector_store_id=vector_store_id),
                    params=params,
                )
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.CREATE_DOCUMENT.value:
                text = arguments.get("text")
                user_provided_name = arguments.get("document_name")
                params = {"text": text, "document_name": user_provided_name}
                data = await client.post(
                    CREATE_DOCUMENT_PATH.format(vector_store_id=vector_store_id),
                    data=params,
                )
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.DELETE_DOCUMENT.value:
                document_id = arguments.get("document_id")
                data = await client.delete(
                    DOCUMENT_PATH.format(
                        vector_store_id=vector_store_id, document_id=document_id
                    ),
                )
                return [types.TextContent(type="text", text=str(data))]
            case VectorStoreTools.MODIFY_DOCUMENT.value:
                document_id = arguments.get("document_id")
                params = {
                    k: v
                    for k, v in {
                        "name": arguments.get("document_name"),
                    }.items()
                    if v is not None
                }
                data = await client.patch(
                    DOCUMENT_PATH.format(
                        vector_store_id=vector_store_id, document_id=document_id
                    ),
                    data=params,
                )
                return [types.TextContent(type="text", text=str(data))]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    return server


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        server = await serve()
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )
