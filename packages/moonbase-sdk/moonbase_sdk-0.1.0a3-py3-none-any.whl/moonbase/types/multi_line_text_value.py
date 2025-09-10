# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MultiLineTextValue"]


class MultiLineTextValue(BaseModel):
    data: str
    """Text which may contain line breaks, can be up to 65,536 characters long.

    Do not use markdown formatting, just plain text.
    """

    type: Literal["value/text/multi_line"]
