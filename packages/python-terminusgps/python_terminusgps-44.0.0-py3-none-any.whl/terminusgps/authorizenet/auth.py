from authorizenet.apicontractsv1 import merchantAuthenticationType
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_merchant_auth() -> merchantAuthenticationType:
    """
    Returns the merchant authentication information for Authorizenet API controller execution.

    :raises ~django.core.exceptions.ImproperlyConfigured: If the :py:data:`MERCHANT_AUTH_LOGIN_ID` or the :py:data:`MERCHANT_AUTH_TRANSACTION_KEY` settings weren't set.
    :returns: A merchant authentication object.
    :rtype: ~authorizenet.apicontractsv1.merchantAuthenticationType

    """
    if not all(
        [
            hasattr(settings, "MERCHANT_AUTH_LOGIN_ID"),
            hasattr(settings, "MERCHANT_AUTH_TRANSACTION_KEY"),
        ]
    ):
        error_msg: str = "'MERCHANT_AUTH_LOGIN_ID' and 'MERCHANT_AUTH_TRANSACTION_KEY' settings are required."
        raise ImproperlyConfigured(error_msg)
    return merchantAuthenticationType(
        name=str(settings.MERCHANT_AUTH_LOGIN_ID),
        transactionKey=str(settings.MERCHANT_AUTH_TRANSACTION_KEY),
    )


def get_environment() -> str:
    """
    Returns the environment for Authorizenet API controller execution.

    :raises ~django.core.exceptions.ImproperlyConfigured: If the :py:data:`MERCHANT_AUTH_ENVIRONMENT` setting wasn't set.
    :returns: An Authorizenet API environment string.
    :rtype: str

    """
    if not hasattr(settings, "MERCHANT_AUTH_ENVIRONMENT"):
        error_msg: str = "'MERCHANT_AUTH_ENVIRONMENT' setting is required."
        raise ImproperlyConfigured(error_msg)
    return settings.MERCHANT_AUTH_ENVIRONMENT


def get_validation_mode() -> str:
    """
    Returns the validation mode for Authorizenet API controller execution.

    :raises ~django.core.exceptions.ImproperlyConfigured: If the :py:data:`MERCHANT_AUTH_VALIDATION_MODE` setting wasn't set.
    :returns: An Authorizenet API validation string.
    :rtype: str

    """
    if not hasattr(settings, "MERCHANT_AUTH_VALIDATION_MODE"):
        error_msg: str = "'MERCHANT_AUTH_VALIDATION_MODE' setting is required."
        raise ImproperlyConfigured(error_msg)
    return settings.MERCHANT_AUTH_VALIDATION_MODE
