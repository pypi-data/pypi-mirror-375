from abc import ABC
from functools import cached_property

from authorizenet import apicontractsv1
from authorizenet.apicontrollersbase import APIOperationBase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import (
    get_environment,
    get_merchant_auth,
    get_validation_mode,
)
from terminusgps.authorizenet.controllers import execute_controller


class AuthorizenetService(ABC):
    """Base class for services that interact with the Authorizenet API."""

    REQUIRED_SETTINGS = (
        "MERCHANT_AUTH_ENVIRONMENT",
        "MERCHANT_AUTH_LOGIN_ID",
        "MERCHANT_AUTH_TRANSACTION_KEY",
        "MERCHANT_AUTH_VALIDATION_MODE",
    )

    def __init__(self) -> None:
        for setting in self.REQUIRED_SETTINGS:
            if not hasattr(settings, setting):
                raise ImproperlyConfigured(f"'{setting}' setting is required.")

    def execute_controller(
        self, controller: APIOperationBase
    ) -> ObjectifiedElement:
        """
        Executes an Authorizenet API controller.

        :param controller: An Authorizenet controller.
        :type controller: ~authorizenet.apicontrollersbase.APIOperationBase
        :raises ~terminusgps.authorizenet.controllers.AuthorizenetControllerExecutionError: If the API call failed.
        :returns: The Authorizenet API controller response.
        :rtype: ~lxml.objectify.ObjectifiedElement

        """
        controller.setenvironment(self.environment)
        controller.setmerchantauthentication(self.merchantAuthentication)
        return execute_controller(controller)

    @cached_property
    def merchantAuthentication(
        self,
    ) -> apicontractsv1.merchantAuthenticationType:
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
