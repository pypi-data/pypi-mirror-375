# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatetimeValueParam"]


class DatetimeValueParam(TypedDict, total=False):
    data: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    type: Required[Literal["value/datetime"]]
