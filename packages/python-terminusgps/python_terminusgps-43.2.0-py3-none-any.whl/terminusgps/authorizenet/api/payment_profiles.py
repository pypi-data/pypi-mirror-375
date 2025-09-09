from authorizenet import apicontractsv1, apicontrollers
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import (
    get_merchant_auth,
    get_validation_mode,
)
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_customer_payment_profile",
    "get_customer_payment_profile",
    "validate_customer_payment_profile",
    "update_customer_payment_profile",
    "delete_customer_payment_profile",
]


def create_customer_payment_profile(
    customer_profile_id: int,
    payment_profile: apicontractsv1.customerPaymentProfileType,
    validate: bool = True,
) -> ObjectifiedElement | None:
    """
    `createCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-create-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: int
    :param payment_profile: An Authorizenet payment profile element.
    :type payment_profile: ~authorizenet.apicontractsv1.customerPaymentProfileType
    :param validate: Whether to validate the payment profile. Default is True.
    :returns: An Authorizenet createCustomerPaymentProfileResponse element.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    request = apicontractsv1.createCustomerPaymentProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.paymentProfile = payment_profile
    if validate:
        request.validationMode = get_validation_mode()

    return execute_controller(
        apicontrollers.createCustomerPaymentProfileController(request)
    )


def get_customer_payment_profile(
    customer_profile_id: int,
    payment_profile_id: int,
    include_issuer_info: bool = False,
) -> ObjectifiedElement | None:
    """
    `getCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-get-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: int
    :param payment_profile_id: An Authorizenet customer payment profile id.
    :type payment_profile_id: int
    :param include_issuer_info: Whether to include issuer info in the response. Default is False.
    :type include_issuer_info: bool
    :returns: An Authorizenet getCustomerPaymentProfileResponse element.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    request = apicontractsv1.getCustomerPaymentProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.customerPaymentProfileId = str(payment_profile_id)
    request.includeIssuerInfo = str(include_issuer_info).lower()

    return execute_controller(
        apicontrollers.getCustomerPaymentProfileController(request)
    )


def validate_customer_payment_profile(
    customer_profile_id: int, payment_profile_id: int
) -> ObjectifiedElement | None:
    """
    `validateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-validate-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: int
    :param payment_profile_id: An Authorizenet customer payment profile id.
    :type payment_profile_id: int
    :returns: An Authorizenet validateCustomerPaymentProfileResponse element.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    request = apicontractsv1.validateCustomerPaymentProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.customerPaymentProfileId = str(payment_profile_id)
    request.validationMode = get_validation_mode()

    return execute_controller(
        apicontrollers.validateCustomerPaymentProfileController(request)
    )


def update_customer_payment_profile(
    customer_profile_id: int,
    payment_profile_id: int,
    payment_profile: apicontractsv1.customerPaymentProfileType,
    validate: bool = True,
) -> ObjectifiedElement | None:
    """
    `updateCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-update-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: int
    :param payment_profile_id: An Authorizenet customer payment profile id.
    :type payment_profile_id: int
    :param payment_profile: An Authorizenet payment profile element.
    :type payment_profile: ~authorizenet.apicontractsv1.customerPaymentProfileType
    :param validate: Whether to validate the payment profile. Default is True.
    :type validate: bool
    :returns: An Authorizenet updateCustomerPaymentProfileResponse element.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    if not hasattr(payment_profile, "customerPaymentProfileId"):
        payment_profile.customerPaymentProfileId = str(payment_profile_id)

    request = apicontractsv1.updateCustomerPaymentProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.paymentProfile = payment_profile
    if validate:
        request.validationMode = get_validation_mode()

    return execute_controller(
        apicontrollers.updateCustomerPaymentProfileController(request)
    )


def delete_customer_payment_profile(
    customer_profile_id: int, payment_profile_id: int
) -> ObjectifiedElement | None:
    """
    `deleteCustomerPaymentProfileRequest <https://developer.authorize.net/api/reference/index.html#customer-profiles-delete-customer-payment-profile>`_.

    :param customer_profile_id: An Authorizenet customer profile id.
    :type customer_profile_id: int
    :param payment_profile_id: An Authorizenet customer payment profile id.
    :type payment_profile_id: int
    :returns: An Authorizenet deleteCustomerPaymentProfileResponse element.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    request = apicontractsv1.deleteCustomerPaymentProfileRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.customerProfileId = str(customer_profile_id)
    request.customerPaymentProfileId = str(payment_profile_id)

    return execute_controller(
        apicontrollers.deleteCustomerPaymentProfileController(request)
    )
