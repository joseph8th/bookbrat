from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from django.contrib.auth.models import User

from packages.models import Bookstore, Book
from packages.views import BookstoreCreate, BookstoreUpdate, BookstoreDelete

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Bookstore.objects.order_by('id')[:20],
            context_object_name='bookstore_list',
            template_name='packages/index.html'),
        name='bookstore_index'),
)

urlpatterns += patterns('packages.views',
    url(r'^seller/$', 'myaccount'),
    url(r'^seller/stores/$', 'mybookstores', name='mybookstores'),
    url(r'^seller/stores/add/$',
            BookstoreCreate.as_view(), name='bookstore_add'),
    url(r'^seller/stores/(?P<pk>\d+)/update/$',
            BookstoreUpdate.as_view(), name='bookstore_update'),
    url(r'^seller/stores/(?P<pk>\d+)/delete/$',
            BookstoreDelete.as_view(), name='bookstore_delete'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/$',
            'mybookstore_detail', name='bookstore_detail'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/add/$',
            'addbook', name='mybook_add'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/delete/$',
            'deletebook', name='mybook_delete'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/$',
            'mybook_detail', name='mybook_detail'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/results/$',
            'results', name='mybook_results'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/lookup/$',
            'book_lookup', name='mybook_lookup'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/lookup/results/$',
            'book_lookup_results', name='mybook_lookup_results'),
    url(r'^(?P<bookstore_id>\d+)/$', 'viewbookstore'),
#    url(r'^(?P<bookstore_id>\d+)/addbook/$', 'addbook'),
#    url(r'^(?P<bookstore_id>\d+)/deletebook/$', 'deletebook'),
    url(r'^(?P<bookstore_id>\d+)/(?P<book_id>\d+)/$', 'detail'),
    url(r'^(?P<bookstore_id>\d+)/(?P<book_id>\d+)/pricesearch/$', 'pricesearch'),
)
