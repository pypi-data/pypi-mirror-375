# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Error", "Source"]


class Source(BaseModel):
    parameter: Optional[str] = None
    """A string indicating which URI query parameter caused the error."""

    pointer: Optional[str] = None
    """A JSON Pointer [RFC6901] to the associated entity in the request document."""


class Error(BaseModel):
    type: Literal["error"]

    id: Optional[str] = None
    """A unique identifier for this specific error instance."""

    code: Optional[str] = None
    """An application-specific error code string."""

    detail: Optional[str] = None
    """A human-readable explanation of this specific error."""

    source: Optional[Source] = None
    """
    An object containing more specific information about the part of the request
    that caused the error.
    """

    status: Optional[str] = None
    """The HTTP status code for this problem, as a string."""

    title: Optional[str] = None
    """A short, human-readable summary of the problem."""
