from django.views.generic import ListView, DetailView

from oscar_sagepay import models


class Transactions(ListView):
    model = models.RequestResponse
    context_object_name = 'transactions'
    template_name = 'sagepay/dashboard/request_list.html'
    paginate_by = 20


class Transaction(DetailView):
    model = models.RequestResponse
    context_object_name = 'txn'
    template_name = 'sagepay/dashboard/request_detail.html'
