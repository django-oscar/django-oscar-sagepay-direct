================================
Sagepay package for django-oscar
================================

This package provides integration between django-oscar and Sagepay's Direct
APIs.  It is still in the early stage of development - please ask any questions
using the Oscar mailing list:  django-oscar@googlegroups.com.

Continuous integration status:

.. image:: https://secure.travis-ci.org/django-oscar/django-oscar-sagepay-direct.png?branch=master
    :target: http://travis-ci.org/#!/django-oscar/django-oscar-sagepay-direct

Installation
------------

Install package using either:

.. code-block:: bash

   $ pip install django-oscar-sagepay-direct  # not ready just yet sorry 

or:

.. code-block:: bash

   $ pip install git+git://github.com/tangentlabs/django-oscar-sagepay-direct#egg=django-oscar-sagepay-direct

Add ``oscar_sagepay`` to ``INSTALLED_APPS`` and specify your vendor name:

.. code-block:: python

   OSCAR_SAGEPAY_VENDOR = 'tangentlabs'

You will also need to install ``django-oscar`` too.

Usage
-----

The main entry point into this package is the ``oscar_sagepay.facade`` module,
which provides the following functionality:

Authenticate
~~~~~~~~~~~~

Perform an 'AUTHENTICATE' request:

.. code-block:: python

   from decimal import Decimal as D
   from oscar_sagepay import facade

   tx_id = facade.authenticate(amount, currency, bankcard, shipping_address, 
                               billing_address, description, order_number)

where:

- ``amount`` is a ``decimal.Decimal`` instance
- ``currency`` is the 3 character currency code
- ``bankcard`` is an ``oscar.apps.payment.models.Bankcard`` instance
- ``shipping_address`` is an ``oscar.apps.order.models.ShippingAddress``
  instance
- ``billing_address`` is an ``oscar.apps.order.models.BillingAddress``
  instance
- ``description`` (optional) is a short description of the transaction
- ``order_number`` (optional) is an order number associated with the transaction

Authorise
~~~~~~~~~

Perform an 'AUTHORISE' request:

.. code-block:: python

   from decimal import Decimal as D
   from oscar_sagepay import facade

   tx_id = facade.authorise(tx_id, amount, description, order_number)

where:

- ``tx_id`` is the transaction ID of a successful AUTHENTICATE request
- ``amount`` is a ``decimal.Decimal`` instance
- ``description`` (optional) is a short description of the transaction
- ``order_number`` (optional) is an order number associated with the transaction

Refund
~~~~~~

Perform a 'REFUND' request against a previous 'AUTHORISE':

.. code-block:: python

   from decimal import Decimal as D
   from oscar_sagepay import facade

   tx_id = refund(tx_id, amount, description, order_number)

where:

- ``tx_id`` is the transaction ID of a successful AUTHORISE request
- ``amount`` is a ``decimal.Decimal`` instance
- ``description`` (optional) is a short description of the transaction
- ``order_number`` (optional) is an order number associated with the transaction

Void
~~~~

Perform a 'VOID' request against a previous 'AUTHORISE':

.. code-block:: python

   from decimal import Decimal as D
   from oscar_sagepay import facade

   tx_id = void(tx_id, order_number)

where:

- ``tx_id`` is the transaction ID of a successful AUTHORISE request
- ``order_number`` (optional) is an order number associated with the transaction

Checkout
~~~~~~~~

For an example of how this facade can be used used in an Oscar site, see the 
sandbox site that is part of this repo.

Settings
--------

These settings are available:

- ``OSCAR_SAGEPAY_VENDOR`` - your vendor name (passed as ``Vendor`` to Sagepay).
- ``OSCAR_SAGEPAY_VPS_PROTOCOL`` (default: ``3.0``) - the VPS protocol (passed as ``VPSProtocol``
  to Sagepay).
- ``OSCAR_SAGEPAY_TEST_MODE`` (default: ``True``) - whether to use the live or
  test Sagepay servers.
- ``OSCAR_SAGEPAY_TX_CODE_PREFIX`` (default: ``oscar``) - a prefix string to
  prepend to generated TX codes
- ``OSCAR_SAGEPAY_AVSCV2`` (default: ``2``) - the Sagepay setting for AV2CV2
  behaviour.

Contributing
------------

Install locally by creating a virtualenv and running:

.. code-block:: bash

   (sagepay) $ make 

Run tests with:

.. code-block:: bash

   (sagepay) $ py.test 

To run end-to-end tests, you'll need a test account with Sagepay configured to respond
to your IP address and to not response randomly to DIRECT requests (as is the
default). Set your vendor name in ``sandbox/private_settings.py`` and run:

.. code-block:: bash

   (sagepay) $ py.test --external 

Build a sandbox site using:

.. code-block:: bash

   (sagepay) $ make sandbox 

and run the server using:

.. code-block:: bash

   (sagepay) $ sandbox/manage.py runserver

