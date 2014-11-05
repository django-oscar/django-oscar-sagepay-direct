from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required

from oscar.core.application import Application
from . import views

try:
    from oscar.apps.dashboard.nav import register, Node
except ImportError:
    pass
else:
    # Old way of registering Dashboard nodes
    node = Node('Datacash', 'sagepay-transaction-list')
    register(node, 100)


class SagepayDashboard(Application):
    name = None
    list_view = views.Transactions
    detail_view = views.Transaction

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^transactions/$', self.list_view.as_view(),
                name='sagepay-transaction-list'),
            url(r'^transactions/(?P<pk>\d+)/$', self.detail_view.as_view(),
                name='sagepay-transaction-detail'),
        )
        return self.post_process_urls(urlpatterns)

    def get_url_decorator(self, url_name):
        return staff_member_required


application = SagepayDashboard()
