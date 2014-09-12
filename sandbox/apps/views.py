from django.views import generic
from django import shortcuts, http
from django.core.urlresolvers import reverse
from django.contrib import messages
from oscar.apps.order import models as order_models
from oscar.apps.payment import exceptions

from oscar_sagepay import facade, models, gateway


class AuthorisePayment(generic.View):

    def post(self, request, number):
        order = shortcuts.get_object_or_404(
            order_models.Order, number=number)

        # Grab Sagepay TX ID (in a hacky way)
        source = order.sources.all()[0]
        tx_id = source.reference

        url = reverse('dashboard:order-detail', kwargs={
            'number': order.number})
        response = http.HttpResponseRedirect(url)
        try:
            new_tx_id = facade.authorise(tx_id, order_number=order.number)
        except exceptions.PaymentError as e:
            messages.error(
                request, (
                    "We were unable to authorise your order: %s") % e)
            return response

        # Update payment source
        source.debit(reference=new_tx_id)

        messages.success(
            request, "Transaction authorised: TX ID %s" % new_tx_id)
        return response


class RefundPayment(generic.View):

    def post(self, request, number):
        order = shortcuts.get_object_or_404(
            order_models.Order, number=number)

        # Grab first AUTHORISE txn to refund
        txns = models.RequestResponse.objects.filter(
            reference=order.number, tx_type=gateway.TXTYPE_AUTHORISE,
            status='OK')
        txn = txns[0]

        url = reverse('dashboard:order-detail', kwargs={
            'number': order.number})
        response = http.HttpResponseRedirect(url)
        try:
            new_tx_id = facade.refund(txn.tx_id, order_number=order.number)
        except exceptions.PaymentError as e:
            messages.error(
                request, (
                    "We were unable to refund your order: %s") % e)
            return response

        # Update payment source
        source = order.sources.all()[0]
        source.refund(source.amount_debited, reference=new_tx_id)

        messages.success(
            request, "Transaction authorised: TX ID %s" % new_tx_id)
        return response


class VoidPayment(generic.View):

    def post(self, request, number):
        order = shortcuts.get_object_or_404(
            order_models.Order, number=number)

        txns = models.RequestResponse.objects.filter(
            reference=order.number, tx_type=gateway.TXTYPE_AUTHORISE,
            status='OK')
        txn = txns[0]

        url = reverse('dashboard:order-detail', kwargs={
            'number': order.number})
        response = http.HttpResponseRedirect(url)
        try:
            facade.void(txn.tx_id, order_number=order.number)
        except exceptions.PaymentError as e:
            messages.error(
                request, (
                    "We were unable to void your order: %s") % e)
            return response

        messages.success(
            request, "Transaction voided")
        return response
