# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DomainValue"]


class DomainValue(BaseModel):
    data: str
    """A valid internet domain name, without protocol (e.g., 'https://') or path."""

    type: Literal["value/uri/domain"]
