import os
import typing

import wialon.api


class WialonAPIError(Exception):
    """Raised when a Wialon API call fails."""

    def __init__(self, message, *args, **kwargs) -> None:
        self.message = message
        self._code = int(message._code)
        super().__init__(message, *args, **kwargs)

    @property
    def code(self) -> int:
        """Wialon API error code."""
        return self._code


class Wialon(wialon.api.Wialon):
    def call(self, *argc, **kwargs) -> dict[str, typing.Any]:
        try:
            return super().call(*argc, **kwargs)
        except wialon.api.WialonError as e:
            raise WialonAPIError(e)


class WialonSession:
    def __init__(
        self,
        token: str | None = None,
        sid: str | None = None,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
    ) -> None:
        """
        Starts or continues a Wialon API session.

        :param token: A Wialon API token. If not provided, the environment variable ``"WIALON_TOKEN"`` is used.
        :type token: str | None
        :param sid: An optional Wialon API session id. If provided, the session is continued.
        :type sid: str | None
        :param scheme: HTTP request scheme to use. Default is ``"https"``.
        :type scheme: str
        :param host: Wialon API host url. Default is ``"hst-api.wialon.com"``.
        :type host: str
        :param port: Wialon API port. Default is ``443``.
        :type port: int
        :returns: Nothing.
        :rtype: None

        """

        self._token = token if token else os.getenv("WIALON_TOKEN")
        self._username = None
        self._uid = None
        self._wialon_api = Wialon(
            scheme=scheme, host=host, port=port, sid=sid, token=self.token
        )

    def __str__(self) -> str:
        return f"Session #{self.id}"

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        """
        Logs into the Wialon API using :py:meth:`login`.

        :raises AssertionError: If the session's Wialon API :py:attr:`token` wasn't set.
        :returns: A valid Wialon API session.
        :rtype: ~terminusgps.wialon.session.WialonSession

        """
        assert self.token, "Wialon API token wasn't set."
        self.login(self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Logs out of the session by calling :py:meth:`logout`.

        :returns: Nothing.
        :rtype: None

        """
        self.logout()

    @property
    def wialon_api(self) -> Wialon:
        return self._wialon_api

    @property
    def uid(self) -> str | None:
        """
        User id of the session's authenticated Wialon user.

        :type: str | None
        :value: None
        """
        return self._uid

    @property
    def username(self) -> str | None:
        """
        Username of the session's authenticated Wialon user.

        :type: str | None
        :value: None

        """
        return self._username

    @property
    def id(self) -> str | None:
        """
        Wialon API session id.

        Shortcut property for :py:attr:`WialonSession.wialon_api.sid`.

        Returns :py:obj:`None` if the session wasn't logged in.

        :type: str | None
        :value: None

        """
        return self.wialon_api.sid

    @property
    def token(self) -> str:
        """
        Wialon API token set during :py:meth:`WialonSession.__init__`.

        :type: str

        """
        return str(self._token)

    def login(self, token: str, flags: int | None = None) -> str:
        """
        Logs into the Wialon API, starts a new session then returns its id.

        :param token: An active Wialon API token.
        :type token: str
        :param flags: A login response flag integer.
        :type flags: int
        :raises WialonError: If the login fails.
        :raises AssertionError: If the login token was not set.
        :returns: The new session id.
        :rtype: str

        """
        try:
            response = self.wialon_api.token_login(
                **{"token": token, "fl": flags if flags else 0x2}
            )
            self._set_login_response(response)
            return response.get("eid", "")
        except (wialon.api.WialonError, ValueError):
            print("Failed to login to the Wialon API.")
            raise

    def logout(self) -> None:
        """
        Logs out of the Wialon API session.

        :returns: Nothing.
        :rtype: None

        """
        sid = self.wialon_api.sid
        response = self.wialon_api.core_logout({})

        if response.get("error") != 0:
            print(
                f"Failed to properly logout of session #{sid}: '{response.get('message')}'"
            )
        self.wialon_api.sid = None

    def _set_login_response(self, login_response: dict | None = None) -> None:
        """
        Sets the Wialon API session's attributes based on a login response.

        :param login_response: A dictionary returned from :py:meth:`login`.
        :type login_response: dict
        :raises ValueError: If ``login_response`` wasn't provided.
        :returns: Nothing.
        :rtype: None

        """
        if login_response is None:
            raise ValueError(
                f"Login response is required, got '{login_response}'"
            )

        self.wialon_api.sid = login_response.get("eid")
        self._uid = login_response.get("user", {}).get("id")
        self._username = login_response.get("au")
