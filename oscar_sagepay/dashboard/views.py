from django.views.generic import ListView, DetailView
from django.db.models import Q

from oscar_sagepay import models
from . import forms


class Transactions(ListView):
    model = models.RequestResponse
    context_object_name = 'transactions'
    template_name = 'sagepay/dashboard/request_list.html'
    paginate_by = 20
    form_class = forms.TransactionSearch
    query = None

    def get(self, request, *args, **kwargs):
        self.form = self.form_class(request.GET)
        return super(Transactions, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # Allow txns to be filtered by matching against the vendor code and the
        # Sagepay TX ID.
        qs = super(Transactions, self).get_queryset()
        if self.form.is_valid():
            self.query = self.form.cleaned_data['q']
            filters = (Q(vendor_tx_code__startswith=self.query) |
                       Q(tx_id__contains=self.query))
            qs = qs.filter(filters)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(Transactions, self).get_context_data(**kwargs)
        ctx['form'] = self.form
        ctx['query'] = self.query
        return ctx


class Transaction(DetailView):
    model = models.RequestResponse
    context_object_name = 'txn'
    template_name = 'sagepay/dashboard/request_detail.html'
