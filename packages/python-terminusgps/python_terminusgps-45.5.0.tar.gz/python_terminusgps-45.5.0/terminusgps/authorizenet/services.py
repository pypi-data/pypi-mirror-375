from abc import ABC
from functools import cached_property
from typing import Callable

from authorizenet.apicontractsv1 import merchantAuthenticationType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from lxml.objectify import ObjectifiedElement

from .auth import get_environment, get_merchant_auth, get_validation_mode
from .controllers import execute_controller


class AuthorizenetService(ABC):
    """Base class for services that interact with the Authorizenet API."""

    REQUIRED_SETTINGS = (
        "MERCHANT_AUTH_ENVIRONMENT",
        "MERCHANT_AUTH_LOGIN_ID",
        "MERCHANT_AUTH_TRANSACTION_KEY",
        "MERCHANT_AUTH_VALIDATION_MODE",
    )

    def __init__(self) -> None:
        """Raises :py:exc:`~django.core.exceptions.ImproperlyConfigured` if required settings weren't set."""
        for setting in self.REQUIRED_SETTINGS:
            if not hasattr(settings, setting):
                raise ImproperlyConfigured(f"'{setting}' setting is required.")

    def call_api(self, func: Callable, *args, **kwargs) -> ObjectifiedElement:
        """
        Calls the Authorizenet API function with arguments and returns the result.

        :param func: An Authorizenet API function.
        :type func: ~typing.Callable
        :param args: Positional arguments for the API call.
        :param kwargs: Keyword arguments for the API call.
        :raises ~terminusgps.authorizenet.controllers.AuthorizenetControllerExecutionError: If the API call failed.
        :returns: The Authorizenet API call response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        request, controller_cls = func(*args, **kwargs)
        request.merchantAuthentication = self.merchantAuthentication
        return execute_controller(controller_cls(request), self.environment)

    @cached_property
    def merchantAuthentication(self) -> merchantAuthenticationType:
        """Merchant authentication element for Authorizenet API requests."""
        return get_merchant_auth()

    @cached_property
    def environment(self) -> str:
        """Environment for Authorizenet API requests."""
        return get_environment()

    @cached_property
    def validationMode(self) -> str:
        """Validation mode for Authorizenet API requests."""
        return get_validation_mode()
