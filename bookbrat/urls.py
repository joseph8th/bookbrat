import settings
import registration

from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import ListView
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from packages.models import Bookstore, Book

admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Bookstore.objects.order_by('id')[:20],
            context_object_name='bookstore_list',
            template_name='packages/index.html'),
        name='bookstore_index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^profiles/', include('profiles.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^packages/', include('packages.urls')),
)

urlpatterns += staticfiles_urlpatterns()
