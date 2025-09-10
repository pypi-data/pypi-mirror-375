# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import TypeAlias

from .value import Value
from .geo_value import GeoValue
from .url_value import URLValue
from .date_value import DateValue
from .email_value import EmailValue
from .float_value import FloatValue
from .choice_value import ChoiceValue
from .domain_value import DomainValue
from .boolean_value import BooleanValue
from .integer_value import IntegerValue
from .datetime_value import DatetimeValue
from .monetary_value import MonetaryValue
from .relation_value import RelationValue
from .social_x_value import SocialXValue
from .percentage_value import PercentageValue
from .telephone_number import TelephoneNumber
from .funnel_step_value import FunnelStepValue
from .multi_line_text_value import MultiLineTextValue
from .single_line_text_value import SingleLineTextValue
from .social_linked_in_value import SocialLinkedInValue

__all__ = ["FieldValue"]

FieldValue: TypeAlias = Union[
    SingleLineTextValue,
    MultiLineTextValue,
    IntegerValue,
    FloatValue,
    MonetaryValue,
    PercentageValue,
    BooleanValue,
    EmailValue,
    URLValue,
    DomainValue,
    SocialXValue,
    SocialLinkedInValue,
    TelephoneNumber,
    GeoValue,
    DateValue,
    DatetimeValue,
    ChoiceValue,
    FunnelStepValue,
    RelationValue,
    List[Value],
]
