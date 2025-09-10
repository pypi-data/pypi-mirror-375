# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["ProgramMessageSendParams", "Person"]


class ProgramMessageSendParams(TypedDict, total=False):
    person: Required[Person]
    """The person to send the message to."""

    program_template_id: Required[str]
    """The ID of the `ProgramTemplate` to use for sending the message."""

    custom_variables: Dict[str, object]
    """Any custom Liquid variables to be interpolated into the message template."""


class Person(TypedDict, total=False):
    email: Required[str]
