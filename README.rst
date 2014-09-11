================================
Sagepay package for django-oscar
================================

This package provides integration between django-oscar and Sagepay's Direct
APIs.  It is still in the early stage of development - please ask any questions
using the Oscar mailing list:  django-oscar@googlegroups.com.

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
