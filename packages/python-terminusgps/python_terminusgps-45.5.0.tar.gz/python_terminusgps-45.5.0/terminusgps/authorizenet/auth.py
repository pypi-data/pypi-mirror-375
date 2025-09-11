from authorizenet.apicontractsv1 import merchantAuthenticationType
from django.conf import settings


def get_merchant_auth() -> merchantAuthenticationType:
    """
    Returns the merchant authentication information for Authorizenet API controller execution.

    :returns: A merchant authentication object.
    :rtype: ~authorizenet.apicontractsv1.merchantAuthenticationType

    """
    return merchantAuthenticationType(
        name=str(settings.MERCHANT_AUTH_LOGIN_ID),
        transactionKey=str(settings.MERCHANT_AUTH_TRANSACTION_KEY),
    )


def get_environment() -> str:
    """
    Returns the environment for Authorizenet API controller execution.

    :returns: An Authorizenet API environment string.
    :rtype: str

    """
    return settings.MERCHANT_AUTH_ENVIRONMENT


def get_validation_mode() -> str:
    """
    Returns the validation mode for Authorizenet API controller execution.

    :returns: An Authorizenet API validation string.
    :rtype: str

    """
    return settings.MERCHANT_AUTH_VALIDATION_MODE
