Usage
=====

Check the Authorizenet API documentation for expected attributes in each response.

.. code:: python

    from terminusgps.authorizenet import api as anet

    # An Authorizenet 'createCustomerProfileRequest'
    response = anet.create_customer_profile(
        merchant_id="1",
        email="blake@terminusgps.com",
        description="Blake Nall"
    )

    # Authorizenet API calls may return None
    # Check first before trying to access attributes on it
    if response is not None and hasattr(response, "customerProfileId"):
        response.customerProfileId
