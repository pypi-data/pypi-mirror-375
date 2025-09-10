# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ProgramRetrieveParams"]


class ProgramRetrieveParams(TypedDict, total=False):
    include: List[Literal["activity_metrics", "program_template"]]
    """Specifies which related objects to include in the response.

    Valid options are `activity_metrics` and `program_template`.
    """
