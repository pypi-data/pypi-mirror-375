from authorizenet import apicontractsv1, apicontrollers
from lxml.objectify import ObjectifiedElement

from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.authorizenet.controllers import execute_controller

__all__ = [
    "create_subscription",
    "get_subscription",
    "get_subscription_status",
    "update_subscription",
    "cancel_subscription",
]


def create_subscription(
    subscription: apicontractsv1.ARBSubscriptionType,
) -> ObjectifiedElement | None:
    """
    `ARBCreateSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-create-a-subscription>`_.

    :param subscription: An Authorizenet ARBSubscriptionType element.
    :type subscription: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`
    :returns: An Authorizenet ARBCreateSubscriptionResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.ARBCreateSubscriptionRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscription = subscription

    return execute_controller(
        apicontrollers.ARBCreateSubscriptionController(request)
    )


def get_subscription(
    subscription_id: int, include_transactions: bool = True
) -> ObjectifiedElement | None:
    """
    `ARBGetSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-get-subscription>`_.

    :param subscription_id: An Authorizenet subscription id.
    :type subscription_id: :py:obj:`int`
    :param include_transactions: Whether to include the subscription transaction list in the response. Default is :py:obj:`True`.
    :type include_transactions: :py:obj:`bool`
    :returns: An Authorizenet ARBGetSubscriptionResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.ARBGetSubscriptionRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscriptionId = str(subscription_id)
    request.includeTransactions = str(include_transactions).lower()

    return execute_controller(
        apicontrollers.ARBGetSubscriptionController(request)
    )


def get_subscription_status(subscription_id: int) -> ObjectifiedElement | None:
    """
    `ARBGetSubscriptionStatusRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-get-subscription-status>`_.

    :param subscription_id: An Authorizenet subscription id.
    :type subscription_id: :py:obj:`int`
    :returns: An Authorizenet ARBGetSubscriptionStatusResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.ARBGetSubscriptionStatusRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscriptionId = str(subscription_id)

    return execute_controller(
        apicontrollers.ARBGetSubscriptionStatusController(request)
    )


def update_subscription(
    subscription_id: int, subscription: apicontractsv1.ARBSubscriptionType
) -> ObjectifiedElement | None:
    """
    `ARBUpdateSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-update-a-subscription>`_.

    :param subscription_id: An Authorizenet subscription id.
    :type subscription_id: :py:obj:`int`
    :param subscription: An Authorizenet ARBSubscriptionType element.
    :type subscription: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`
    :returns: An Authorizenet ARBUpdateSubscriptionResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.ARBUpdateSubscriptionRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscriptionId = str(subscription_id)
    request.subscription = subscription

    return execute_controller(
        apicontrollers.ARBUpdateSubscriptionController(request)
    )


def cancel_subscription(subscription_id: int) -> ObjectifiedElement | None:
    """
    `ARBCancelSubscriptionRequest <https://developer.authorize.net/api/reference/index.html#recurring-billing-cancel-a-subscription>`_.

    :param subscription_id: An Authorizenet subscription id.
    :type subscription_id: :py:obj:`int`
    :returns: An Authorizenet ARBCancelSubscriptionResponse element.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement` | :py:obj:`None`

    """
    request = apicontractsv1.ARBCancelSubscriptionRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscriptionId = str(subscription_id)

    return execute_controller(
        apicontrollers.ARBCancelSubscriptionController(request)
    )
