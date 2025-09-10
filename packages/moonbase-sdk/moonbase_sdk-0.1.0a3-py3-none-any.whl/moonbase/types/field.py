# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from .._utils import PropertyInfo
from .geo_field import GeoField
from .url_field import URLField
from .date_field import DateField
from .email_field import EmailField
from .float_field import FloatField
from .stage_field import StageField
from .choice_field import ChoiceField
from .domain_field import DomainField
from .boolean_field import BooleanField
from .integer_field import IntegerField
from .datetime_field import DatetimeField
from .monetary_field import MonetaryField
from .relation_field import RelationField
from .social_x_field import SocialXField
from .percentage_field import PercentageField
from .multi_line_text_field import MultiLineTextField
from .single_line_text_field import SingleLineTextField
from .social_linked_in_field import SocialLinkedInField
from .telephone_number_field import TelephoneNumberField

__all__ = ["Field"]

Field: TypeAlias = Annotated[
    Union[
        SingleLineTextField,
        MultiLineTextField,
        IntegerField,
        FloatField,
        MonetaryField,
        PercentageField,
        BooleanField,
        EmailField,
        URLField,
        DomainField,
        SocialXField,
        SocialLinkedInField,
        TelephoneNumberField,
        GeoField,
        DateField,
        DatetimeField,
        ChoiceField,
        StageField,
        RelationField,
    ],
    PropertyInfo(discriminator="type"),
]
