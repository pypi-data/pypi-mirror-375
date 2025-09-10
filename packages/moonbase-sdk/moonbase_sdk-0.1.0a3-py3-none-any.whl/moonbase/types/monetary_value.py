# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MonetaryValue", "Data"]


class Data(BaseModel):
    currency: str
    """The 3-letter ISO 4217 currency code"""

    in_minor_units: int
    """The amount in the minor units of the currency.

    For example, $10 (10 USD) would be 1000. Minor units conversion depends on the
    currency.
    """


class MonetaryValue(BaseModel):
    data: Data
    """
    A monetary amount is composed of the amount in the smallest unit of a currency
    and an ISO currency code.
    """

    type: Literal["value/number/monetary"]
