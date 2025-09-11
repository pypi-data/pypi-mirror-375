from authorizenet.apicontrollersbase import APIOperationBase
from lxml.objectify import ObjectifiedElement


def execute_controller(
    controller: APIOperationBase, environment: str
) -> ObjectifiedElement | None:
    """
    Executes an Authorizenet API controller and returns its response.

    :param controller: An Authorizenet API controller.
    :type controller: ~authorizenet.apicontrollersbase.APIOperationBase
    :param environment: Authorizenet environment to execute the controller in.
    :type environment: :py:obj:`str`
    :param merchant_auth: Authorizenet merchant authentication element.
    :type merchant_auth: ~authorizenet.apicontractsv1.merchantAuthenticationType
    :raises AuthorizenetControllerExecutionError: If the API call fails.
    :returns: An Authorizenet API response, if any.
    :rtype: ~lxml.objectify.ObjectifiedElement | None

    """
    controller.setenvironment(environment)
    controller.execute()
    response = controller.getresponse()

    if response is None:
        raise AuthorizenetControllerExecutionError(
            message="Authorizenet controller response didn't exist.", code="1"
        )
    if response is not None and response.messages.resultCode != "Ok":
        raise AuthorizenetControllerExecutionError(
            message=response.messages.message[0]["text"].text,
            code=response.messages.message[0]["code"].text,
        )
    return response


class AuthorizenetControllerExecutionError(Exception):
    """Raised when an Authorizenet API controller fails to execute."""

    def __init__(self, message: str, code: str, *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)
        self._message = message
        self._code = code

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    @property
    def message(self) -> str:
        """An Authorizenet API error message."""
        return self._message

    @property
    def code(self) -> str:
        """An Authorizenet API error code."""
        return self._code
