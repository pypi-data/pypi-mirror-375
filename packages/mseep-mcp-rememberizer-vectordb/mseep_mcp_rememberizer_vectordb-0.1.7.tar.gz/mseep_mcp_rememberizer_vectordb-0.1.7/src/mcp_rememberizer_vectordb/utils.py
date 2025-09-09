import logging
from enum import Enum

import httpx
from dotenv import load_dotenv
from httpx import HTTPError, HTTPStatusError, Timeout
from mcp import McpError

logger = logging.getLogger(__name__)
load_dotenv()

APP_NAME = "mcp_rememberizer_vectordb"
ME_VECTOR_STORE_PATH = "vector-stores/me/"
SEARCH_PATH = "vector-stores/{vector_store_id}/documents/search"
AGENTIC_SEARCH_PATH = "vector-stores/{vector_store_id}/documents/agentic_search"
LIST_DOCUMENTS_PATH = "vector-stores/{vector_store_id}/documents/"
DOCUMENT_PATH = "vector-stores/{vector_store_id}/documents/{document_id}/"
CREATE_DOCUMENT_PATH = "vector-stores/{vector_store_id}/documents/create"


class VectorStoreTools(Enum):
    SEARCH = "rememberizer_vectordb_search"
    AGENTIC_SEARCH = "rememberizer_vectordb_agentic_search"
    VECTOR_DATABASE_INFORMATION = "rememberizer_vectordb_information"
    LIST_DOCUMENTS = "rememberizer_vectordb_list_documents"
    CREATE_DOCUMENT = "rememberizer_vectordb_create_document"
    DELETE_DOCUMENT = "rememberizer_vectordb_delete_document"
    MODIFY_DOCUMENT = "rememberizer_vectordb_modify_document"


class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.http_client = httpx.AsyncClient(
            base_url=base_url,
            timeout=Timeout(connect=60.0, read=60.0, write=5.0, pool=5.0),
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key,
            },
            verify=False,
        )

    async def get(self, path: str, params: dict = None):
        try:
            logger.debug(f"Fetching {path}")
            response = await self.http_client.get(path, params=params)
            if response.status_code == 401:
                raise McpError(
                    "Error: Unauthorized. Please check your REMEMBERIZER API token"
                )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            logger.error(
                f"HTTP {exc.response.status_code} error while fetching {path}: {str(exc)}",
                exc_info=True,
            )
            raise McpError(
                f"Failed to fetch {path}. Status: {exc.response.status_code}"
            )
        except HTTPError as exc:
            logger.error(
                f"Connection error while fetching {path}: {str(exc)}", exc_info=True
            )
            raise McpError(f"Failed to fetch {path}. Connection error.")

    async def post(self, path, data: dict, params: dict = None):
        try:
            logger.debug(f"Posting to {path}")
            response = await self.http_client.post(path, json=data, params=params)
            if response.status_code == 401:
                raise McpError(
                    "Error: Unauthorized. Please check your REMEMBERIZER API token"
                )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            logger.error(
                f"HTTP {exc.response.status_code} error while posting to {path}: {str(exc)}",
                exc_info=True,
            )
            raise McpError(
                f"Failed to post to {path}. Status: {exc.response.status_code}"
            )
        except HTTPError as exc:
            logger.error(
                f"Connection error while posting to {path}: {str(exc)}", exc_info=True
            )
            raise McpError(f"Failed to post to {path}. Connection error.")

    async def delete(self, path: str, params: dict = None):
        try:
            logger.debug(f"Deleting {path}")
            response = await self.http_client.delete(path, params=params)
            if response.status_code == 401:
                raise McpError(
                    "Error: Unauthorized. Please check your REMEMBERIZER API token"
                )
            response.raise_for_status()

            if response.status_code != 204:
                return response.json()
            return None
        except HTTPStatusError as exc:
            logger.error(
                f"HTTP {exc.response.status_code} error while deleting {path}: {str(exc)}",
                exc_info=True,
            )
            raise McpError(
                f"Failed to delete {path}. Status: {exc.response.status_code}"
            )
        except HTTPError as exc:
            logger.error(
                f"Connection error while deleting {path}: {str(exc)}", exc_info=True
            )
            raise McpError(f"Failed to delete {path}. Connection error.")

    async def patch(self, path: str, data: dict, params: dict = None):
        try:
            logger.debug(f"Patching {path}")
            response = await self.http_client.patch(path, json=data, params=params)
            if response.status_code == 401:
                raise McpError(
                    "Error: Unauthorized. Please check your REMEMBERIZER API token"
                )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as exc:
            logger.error(
                f"HTTP {exc.response.status_code} error while patching {path}: {str(exc)}",
                exc_info=True,
            )
            raise McpError(
                f"Failed to patch {path}. Status: {exc.response.status_code}"
            )
        except HTTPError as exc:
            logger.error(
                f"Connection error while patching {path}: {str(exc)}", exc_info=True
            )
            raise McpError(f"Failed to patch {path}. Connection error.")
