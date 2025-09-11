from pydantic import BaseModel, Field, HttpUrl, PositiveInt
from typing import Optional


class ApiErrorResponse(BaseModel):
    """
    Response schema for API failures.
    """

    http_code: PositiveInt = Field(description="The HTTP status code of the failure.")
    message: str = Field(description="The error message describing the failure.")
    code: Optional[str] = Field(default=None, description="The error code describing the failure.")
    source: Optional[str] = Field(default=None, description="The source of the failure.")
    property: Optional[str] = Field(
        default=None, description="The property that caused the failure."
    )


class CustomDomainNewShortUrl(BaseModel):
    id: str = Field(description="The long unique identifier for the custom domain.")


class CreateShortUrlRequest(BaseModel):
    """
    Request schema for creating a new short URL.
    """

    destination: HttpUrl = Field(description="The destination or the long URL to be shortened.")
    slashtag: Optional[str] = Field(
        default=None,
        description="The slug/slashtag or the custom identifier for the short URL.",
        min=1,
        max=40,
    )
    title: Optional[str] = Field(
        default=None,
        description="The title to identify your short URL.",
        min=3,
        max=255,
    )
    domain: Optional[CustomDomainNewShortUrl] = Field(default=None)
    description: Optional[str] = Field(
        default=None,
        description="A description/note to associate with the short link.",
        min=3,
        max=2000,
    )


class ShortUrlDetails(BaseModel):
    """
    Response schema containing the short URL and metadata.
    """

    id: str = Field(
        description="The long unique identifier for the short URL. This is different from the slug/slashtag."
    )
    title: str = Field(description="The title to identify your short URL.")
    destination: HttpUrl = Field(description="The destination or the long URL to be shortened.")
    shortUrl: str = Field(description="The short link pointing to the long/destination URL")


class ShortUrlDetailsList(BaseModel):
    """
    Response schema containing the short URL and metadata.
    """

    urls: list[ShortUrlDetails] = Field(description="List of short URLs along with metadata.")


class CustomDomainListShortUrl(BaseModel):
    id: Optional[str] = Field(
        default=None,
        description="The long unique identifier for the custom domain. This is different from the slug/slashtag.",
    )
    fullName: Optional[str] = Field(
        default=None, description="The fully qualified custom domain name."
    )


class GetOrListShortUrlsRequest(BaseModel):
    """
    Request schema for getting or listing short URLs.
    """

    limit: PositiveInt = Field(
        default=25, description="The maximum number of short URLs to retrieve.", max=25
    )
    last: Optional[str] = Field(
        default=None,
        description="The long unique identifier of the last short URL to retrieve the next set of short URLs.",
    )
    domain: Optional[CustomDomainListShortUrl] = Field(default=None)
    slashtag: Optional[str] = Field(
        default=None,
        description="The slug/slashtag or the custom identifier for the short URL. Custom domain is required to use this field",
    )
    dateFrom: Optional[str] = Field(
        default=None,
        description="The start date to filter short URLs by creation date. Date format must be YYYY-MM-DD",
    )
    dateTo: Optional[str] = Field(
        default=None,
        description="The end date to filter short URLs by creation date. Date format must be YYYY-MM-DD",
    )


class DeleteShortUrlRequest(BaseModel):
    """
    Request schema for deleting a short URL.
    """

    id: str = Field(
        description="The long unique identifier of the short URL. This is different from the slug/slashtag."
    )
