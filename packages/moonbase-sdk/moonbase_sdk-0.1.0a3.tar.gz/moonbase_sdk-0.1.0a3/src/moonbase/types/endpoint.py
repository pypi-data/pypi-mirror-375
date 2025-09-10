# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .subscription import Subscription

__all__ = ["Endpoint"]


class Endpoint(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Time at which the object was created, as an ISO 8601 timestamp in UTC."""

    status: Literal["disabled", "enabled"]
    """Indicates whether the endpoint is enabled."""

    subscriptions: List[Subscription]
    """
    An array of `WebhookSubscription` objects representing the events this endpoint
    will receive.
    """

    type: Literal["webhook_endpoint"]
    """String representing the object’s type.

    Always `webhook_endpoint` for this object.
    """

    updated_at: datetime
    """Time at which the object was last updated, as an ISO 8601 timestamp in UTC."""

    url: str
    """The HTTPS URL where webhook events will be sent."""

    secret: Optional[str] = None
    """The signing secret used to verify webhook authenticity.

    This value is only shown when creating the endpoint and starts with `whsec_`.
    """
