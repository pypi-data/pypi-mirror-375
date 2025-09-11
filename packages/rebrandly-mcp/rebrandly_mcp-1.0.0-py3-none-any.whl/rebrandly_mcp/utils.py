import os
import httpx

from enum import Enum
from loguru import logger
from typing import Any, Optional

from rebrandly_mcp.models import ApiErrorResponse


class RequestMethod(str, Enum):
    """Enum for HTTP request methods."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"


async def make_api_request(
    api_path: str,
    req_method: RequestMethod,
    req_data: Optional[dict[str, Any]] = None,
    query_params: Optional[dict[str, Any]] = None,
) -> dict[str, Any] | None:
    """Make a request to the Rebrandly API with proper error handling."""

    # check for the API key
    api_key = os.environ.get("REBRANDLY_API_KEY", None)
    if not api_key:
        err_msg = "Rebrandly API key not found in environment variables."
        logger.error(err_msg)
        raise KeyError(err_msg)

    url = f"https://api.rebrandly.com/v1/{api_path}"

    headers = {
        "User-Agent": "VimalPaliwal Rebrandly MCP",
        "Content-Type": "application/json",
        "apikey": api_key,
    }

    # make async request to the api server
    async with httpx.AsyncClient() as client:
        try:
            logger.info(f"API URL: {url}")
            logger.info(f"Request data: {req_data}")
            logger.info(f"Query Params: {query_params}")

            request = httpx.Request(
                req_method.value, url, headers=headers, data=req_data, params=query_params
            )
            response = await client.send(request)

            # raise exception for non 2xx http code
            response.raise_for_status()

            logger.info(f"Response: {response.status_code} - {response.json()}")

            return response.json()
        except httpx.HTTPStatusError:
            logger.exception("HTTP request failed.")
            return ApiErrorResponse(
                http_code=response.status_code, message=response.text
            ).model_dump()
        except Exception:
            logger.exception("Rebrandly API request failed.")
            raise
