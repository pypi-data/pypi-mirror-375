from loguru import logger

from rebrandly_mcp.server import mcp
from rebrandly_mcp.utils import make_api_request, RequestMethod
from rebrandly_mcp.models import (
    CreateShortUrlRequest,
    ShortUrlDetails,
    ApiErrorResponse,
    DeleteShortUrlRequest,
    GetOrListShortUrlsRequest,
    ShortUrlDetailsList,
)


@mcp.tool()
async def generate_short_url(
    req_data: CreateShortUrlRequest,
) -> ShortUrlDetails | ApiErrorResponse:
    """
    Generate a new short URL for a given long/destination URL.

    Args:
        req_data: The long/destination URL to shorten along with metadata.

    Returns:
        A short URL for the given long URL if success else error code along with the message.
    """

    logger.info("Making an API request to generate a new short URL...")
    api_response = await make_api_request(
        api_path="links",
        req_method=RequestMethod.POST,
        req_data=req_data.model_dump_json(exclude_none=True),
    )

    if "http_code" in api_response:
        return ApiErrorResponse(**api_response)
    else:
        return ShortUrlDetails(**api_response)


@mcp.tool()
async def delete_short_url(
    req_data: DeleteShortUrlRequest,
) -> ShortUrlDetails | ApiErrorResponse:
    """
    Delete an existing short URL.

    Args:
        req_data: The unique identifier of the short URL.

    Returns:
        The deleted short URL and the metadata if success else error code along with the message.
    """

    logger.info("Making an API request to delete the existing short URL...")
    api_response = await make_api_request(
        api_path=f"links/{req_data.id}", req_method=RequestMethod.DELETE
    )

    if "http_code" in api_response:
        return ApiErrorResponse(**api_response)
    else:
        return ShortUrlDetails(**api_response)


@mcp.tool()
async def get_or_list_short_url(
    req_data: GetOrListShortUrlsRequest = None,
) -> ShortUrlDetailsList | ApiErrorResponse:
    """
    Get a single short URL or list multiple short links.

    Args:
        req_data: The filters to use while fetching the short URL(s).

    Returns:
        The list of short URL(s) if success else error code along with the message.
    """

    logger.info("Making an API request to get/list the existing short URL(s)...")
    api_response = await make_api_request(
        api_path="links",
        req_method=RequestMethod.GET,
        query_params=req_data.model_dump_json() if req_data else None,
    )

    if "http_code" in api_response:
        return ApiErrorResponse(**api_response)
    else:
        return ShortUrlDetailsList(urls=api_response)
