from authorizenet import apicontractsv1
from authorizenet.constants import constants as anet_constants
from django.db import models
from django.utils.translation import gettext_lazy as _


class SubscriptionStatus(models.TextChoices):
    """An Authorizenet subscription status."""

    ACTIVE = "active", _("Active")
    """Active subscription."""
    EXPIRED = "expired", _("Expired")
    """Expired subscription."""
    SUSPENDED = "suspended", _("Suspended")
    """Suspended subscription."""
    CANCELED = "canceled", _("Canceled")
    """Canceled subscription."""
    TERMINATED = "terminated", _("Terminated")
    """Terminated subscription."""


class SubscriptionIntervalUnit(models.TextChoices):
    """An Authorizenet subscription interval unit."""

    DAYS = apicontractsv1.ARBSubscriptionUnitEnum.days, _("Days")
    """Days interval unit."""
    MONTHS = apicontractsv1.ARBSubscriptionUnitEnum.months, _("Months")
    """Months interval unit."""


class Environment(models.TextChoices):
    """An Authorizenet execution environment."""

    SANDBOX = anet_constants.SANDBOX, _("Sandbox Environment")
    """Sandbox environment."""
    PRODUCTION = anet_constants.PRODUCTION, _("Production Environment")
    """Production environment."""


class ValidationMode(models.TextChoices):
    """An Authorizenet validation mode."""

    TEST = "testMode", _("Test Mode")
    """Test mode."""
    LIVE = "liveMode", _("Live Mode")
    """Live mode."""
