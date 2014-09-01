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

To run end-to-end tests, request a Sagepay Simulator account and configure it to
not response randomly to DIRECT requests.
