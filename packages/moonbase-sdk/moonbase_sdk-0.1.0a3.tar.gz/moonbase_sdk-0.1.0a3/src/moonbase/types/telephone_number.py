# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TelephoneNumber"]


class TelephoneNumber(BaseModel):
    data: str
    """A telephone number in strictly formatted E.164 format.

    Do not include spaces, dashes, or parentheses etc.
    """

    type: Literal["value/telephone_number"]
