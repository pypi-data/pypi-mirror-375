# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SingleLineTextValue"]


class SingleLineTextValue(BaseModel):
    data: str
    """A single line of text, up to 1024 characters long.

    It should not contain line breaks.
    """

    type: Literal["value/text/single_line"]
