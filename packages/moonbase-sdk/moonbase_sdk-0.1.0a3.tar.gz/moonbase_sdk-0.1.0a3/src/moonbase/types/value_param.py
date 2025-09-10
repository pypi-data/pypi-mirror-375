# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .geo_value_param import GeoValueParam
from .url_value_param import URLValueParam
from .date_value_param import DateValueParam
from .email_value_param import EmailValueParam
from .float_value_param import FloatValueParam
from .choice_value_param import ChoiceValueParam
from .domain_value_param import DomainValueParam
from .boolean_value_param import BooleanValueParam
from .integer_value_param import IntegerValueParam
from .datetime_value_param import DatetimeValueParam
from .monetary_value_param import MonetaryValueParam
from .relation_value_param import RelationValueParam
from .percentage_value_param import PercentageValueParam
from .telephone_number_param import TelephoneNumberParam
from .funnel_step_value_param import FunnelStepValueParam
from .multi_line_text_value_param import MultiLineTextValueParam
from .single_line_text_value_param import SingleLineTextValueParam

__all__ = [
    "ValueParam",
    "SocialXValueParam",
    "SocialXValueParamData",
    "SocialLinkedInValueParam",
    "SocialLinkedInValueParamData",
]


class SocialXValueParamData(TypedDict, total=False):
    url: str
    """The full URL to the X profile, starting with 'https://x.com/'"""

    username: str
    """
    The X username, up to 15 characters long, containing only lowercase letters
    (a-z), uppercase letters (A-Z), numbers (0-9), and underscores (\\__). Does not
    include the '@' symbol prefix.
    """


class SocialXValueParam(TypedDict, total=False):
    data: Required[SocialXValueParamData]
    """
    Social media profile information including both the full URL and extracted
    username.
    """

    type: Required[Literal["value/uri/social_x"]]


class SocialLinkedInValueParamData(TypedDict, total=False):
    url: str
    """The full URL to the LinkedIn profile."""

    username: str
    """
    The LinkedIn username, including the prefix 'company/' for company pages or
    'in/' for personal profiles.
    """


class SocialLinkedInValueParam(TypedDict, total=False):
    data: Required[SocialLinkedInValueParamData]
    """The social media profile for the LinkedIn platform"""

    type: Required[Literal["value/uri/social_linked_in"]]


ValueParam: TypeAlias = Union[
    SingleLineTextValueParam,
    MultiLineTextValueParam,
    IntegerValueParam,
    FloatValueParam,
    MonetaryValueParam,
    PercentageValueParam,
    BooleanValueParam,
    EmailValueParam,
    URLValueParam,
    DomainValueParam,
    SocialXValueParam,
    SocialLinkedInValueParam,
    TelephoneNumberParam,
    GeoValueParam,
    DateValueParam,
    DatetimeValueParam,
    ChoiceValueParam,
    FunnelStepValueParam,
    RelationValueParam,
]
