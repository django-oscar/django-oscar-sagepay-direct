from django import forms

from oscar.apps.payment import forms as payment_forms


# Sagepay require the cardholder name and so we add an additional field here.
class BankcardForm(payment_forms.BankcardForm):
    name = forms.CharField(label="Cardholder name")

    class Meta(payment_forms.BankcardForm.Meta):
        fields = ('name', 'number', 'start_month', 'expiry_month',
                  'ccv')

    @property
    def bankcard(self):
        """
        Return an instance of the Bankcard model (unsaved)
        """
        return payment_forms.Bankcard(
            name=self.cleaned_data['name'],
            number=self.cleaned_data['number'],
            expiry_date=self.cleaned_data['expiry_month'],
            start_date=self.cleaned_data['start_month'],
            ccv=self.cleaned_data['ccv'])
