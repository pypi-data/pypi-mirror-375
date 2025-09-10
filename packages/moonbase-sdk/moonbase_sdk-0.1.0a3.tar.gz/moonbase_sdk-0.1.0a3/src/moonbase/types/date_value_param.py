# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DateValueParam"]


class DateValueParam(TypedDict, total=False):
    data: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]

    type: Required[Literal["value/date"]]
