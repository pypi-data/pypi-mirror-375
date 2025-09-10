# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import date
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DateValue"]


class DateValue(BaseModel):
    data: date

    type: Literal["value/date"]
