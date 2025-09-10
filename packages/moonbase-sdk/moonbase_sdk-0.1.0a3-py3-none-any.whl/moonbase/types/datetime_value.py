# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DatetimeValue"]


class DatetimeValue(BaseModel):
    data: datetime

    type: Literal["value/datetime"]
