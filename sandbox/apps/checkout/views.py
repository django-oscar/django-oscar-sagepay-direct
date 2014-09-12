from django import http
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _

from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.payment.models import SourceType, Source
from oscar.apps.payment.forms import BillingAddressForm

from oscar_sagepay import facade, forms


class PaymentDetailsView(OscarPaymentDetailsView):

    def get_context_data(self, **kwargs):
        # Add bankcard and billing address forms to the template context
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        # Create a default form (with some dummy data)
        form = forms.BankcardForm(initial={
            'name': 'Lord Business',
            'number': '4111111111111111',
            'ccv': '123'})
        ctx['bankcard_form'] = kwargs.get(
            'bankcard_form', form)
        ctx['billing_address_form'] = kwargs.get(
            'billing_address_form', BillingAddressForm())
        return ctx

    def handle_payment_details_submission(self, request):
        # Check forms are valid
        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = BillingAddressForm(request.POST)
        if bankcard_form.is_valid() and billing_address_form.is_valid():
            # Forms are valid - render preview with forms hidden in the page
            return self.render_preview(
                request,
                bankcard=bankcard_form.bankcard,
                bankcard_form=bankcard_form,
                billing_address=billing_address_form.save(commit=False),
                billing_address_form=billing_address_form)

        # Form invalid - re-render
        return self.render_payment_details(
            request, bankcard_form=bankcard_form,
            billing_address_form=billing_address_form)

    def handle_place_order_submission(self, request):
        # Check data from hidden forms again to ensure it hasn't been tampered
        # with.
        bankcard_form = forms.BankcardForm(request.POST)
        billing_address_form = BillingAddressForm(request.POST)
        if bankcard_form.is_valid() and billing_address_form.is_valid():
            # Data is ok - submit order
            submission = self.build_submission(
                order_kwargs={
                    'billing_address': billing_address_form.save(commit=False)
                },
                payment_kwargs={
                    'bankcard_form': bankcard_form,
                    'billing_address_form': billing_address_form,
                })
            return self.submit(**submission)

        # If we get here, it means the hidden forms have been tampered with.
        messages.error(request, _("Invalid submission"))
        return http.HttpResponseRedirect(
            reverse('checkout:payment-details'))

    def build_submission(self, **kwargs):
        # Ensure the shipping address is part of the payment keyword args
        submission = super(PaymentDetailsView, self).build_submission(**kwargs)
        submission['payment_kwargs']['shipping_address'] = submission[
            'shipping_address']
        return submission

    def handle_payment(self, order_number, total, bankcard_form,
                       billing_address_form, shipping_address, **kwargs):
        tx_id = facade.authenticate(
            order_number=order_number,
            amount=total.incl_tax, currency=total.currency,
            bankcard=bankcard_form.bankcard,
            shipping_address=shipping_address,
            billing_address=billing_address_form.save(commit=False))

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, __ = SourceType.objects.get_or_create(name='Sagepay')
        source = Source(source_type=source_type,
                        currency=total.currency,
                        amount_allocated=total.incl_tax,
                        reference=tx_id)
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event('authenticate', total.incl_tax)
