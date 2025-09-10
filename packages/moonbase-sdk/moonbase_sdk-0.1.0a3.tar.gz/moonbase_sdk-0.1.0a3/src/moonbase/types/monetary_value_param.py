# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["MonetaryValueParam", "Data"]


class Data(TypedDict, total=False):
    currency: Required[str]
    """The 3-letter ISO 4217 currency code"""

    in_minor_units: Required[int]
    """The amount in the minor units of the currency.

    For example, $10 (10 USD) would be 1000. Minor units conversion depends on the
    currency.
    """


class MonetaryValueParam(TypedDict, total=False):
    data: Required[Data]
    """
    A monetary amount is composed of the amount in the smallest unit of a currency
    and an ISO currency code.
    """

    type: Required[Literal["value/number/monetary"]]
