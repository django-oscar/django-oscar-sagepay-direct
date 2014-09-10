from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from oscar.app import application
from oscar_sagepay.dashboard.app import application as dashboard_app
from apps import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
urlpatterns += i18n_patterns(
    '',
    (r'^dashboard/sagepay/', dashboard_app.urls),
    url(r'^dashboard/orders/(?P<number>[-\w]+)/authorise/',
        views.AuthorisePayment.as_view(), name='sagepay-authorise'),
    (r'', include(application.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
