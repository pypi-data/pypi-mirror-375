Authentication
==============

Authentication for each Authorizenet API call is handled by values defined in a Django ``settings.py`` module.

Required settings:

   +-----------------------------------+---------------+
   | setting                           | type          |
   +===================================+===============+
   | ``MERCHANT_AUTH_ENVIRONMENT``     | :py:obj:`str` |
   +-----------------------------------+---------------+
   | ``MERCHANT_AUTH_LOGIN_ID``        | :py:obj:`str` |
   +-----------------------------------+---------------+
   | ``MERCHANT_AUTH_TRANSACTION_KEY`` | :py:obj:`str` |
   +-----------------------------------+---------------+
   | ``MERCHANT_AUTH_VALIDATION_MODE`` | :py:obj:`str` |
   +-----------------------------------+---------------+

.. automodule:: terminusgps.authorizenet.auth
    :synopsis: Provides functions for authenticating Authorizenet API calls.
    :members:
