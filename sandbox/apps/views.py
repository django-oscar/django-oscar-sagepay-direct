from django.views import generic
from django import shortcuts, http
from django.core.urlresolvers import reverse
from django.contrib import messages
from oscar.apps.order import models
from oscar.apps.payment import exceptions

from oscar_sagepay import facade


class AuthorisePayment(generic.View):

    def post(self, request, number):
        order = shortcuts.get_object_or_404(
            models.Order, number=number)
        # Grab Sagepay TX ID (in a hacky way)
        source = order.sources.all()[0]
        tx_id = source.reference

        url = reverse('dashboard:order-detail', kwargs={
            'number': order.number})
        response = http.HttpResponseRedirect(url)
        try:
            new_tx_id = facade.authorise(tx_id)
        except exceptions.PaymentError as e:
            messages.error(
                request, (
                    "We were unable to authorise your order: %s") % e)
            return response

        # Update payment source
        source.debit()

        messages.success(
            request, "Transaction authorised: TX ID %s" % new_tx_id)
        return response
