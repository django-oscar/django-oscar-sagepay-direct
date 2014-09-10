from django import forms
from django.utils.translation import ugettext_lazy as _


class TransactionSearch(forms.Form):
    q = forms.CharField(label=_("Search for"), required=False)
