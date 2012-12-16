from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
#from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from packages.models import Bookstore, Book
from packages.forms import RequestBookstoreForm, BookForm

from utils.views import RequestCreateView, RequestUpdateView, RequestDeleteView
#from packages.views import BookstoreCreate, BookstoreUpdate, BookstoreDelete
#from packages.views import BookCreate, BookUpdate, BookDelete

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Bookstore.objects.order_by('id')[:20],
            context_object_name='bookstore_list',
            template_name='packages/index.html'),
        name='bookstore_index'),
)

# book seller views
urlpatterns += patterns('packages.views',
    url(r'^seller/$', 'myaccount'),
    url(r'^seller/stores/$', 'mybookstores', name='mybookstores'),
    url(r'^seller/stores/add/$', 
        RequestCreateView.as_view(
            form_class=RequestBookstoreForm,
            model=Bookstore,
            template_name='packages/bookstore_form.html',
            success_message='Bookstore created successfully.'), 
        name='bookstore_add'),
    url(r'^seller/stores/(?P<pk>\d+)/update/$', 
        RequestUpdateView.as_view(
            form_class=RequestBookstoreForm,
            model=Bookstore,
            template_name='packages/bookstore_form.html',
            success_message='Bookstore updated successfully.'),
        name='bookstore_update'),
    url(r'^seller/stores/(?P<pk>\d+)/delete/$', 
        RequestDeleteView.as_view(
            model=Bookstore,
            success_url='/packages/seller/stores',
            template_name='packages/bookstore_confirm_delete.html',
            success_message='Your Bookstore has been deleted successfully.'),
        name='bookstore_delete'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/$',
        'mybookstore_detail', name='bookstore_detail'),

    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/add/$',
        'mybooks_update', name='book_add'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/update/$',
        'mybooks_update', name='book_update'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/delete/$', 
        RequestDeleteView.as_view(
            model=Book,
            success_url='/packages/seller/(?P<bookstore_id>\d+)',
            template_name='packages/bookstore_confirm_delete.html',
            success_message='Your Book has been deleted successfully.'),
        name='book_delete'),
 
   url(r'^seller/stores/(?P<bookstore_id>\d+)/books/action/$',
        'mybooks_action', name='mybooks_action'),
    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/$',
        'mybook_detail', name='mybook_detail'),

    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/results/$',
        'results', name='mybook_results'),
#    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/lookup/$',
#        'book_lookup', name='mybook_lookup'),
#    url(r'^seller/stores/(?P<bookstore_id>\d+)/books/(?P<book_id>\d+)/lookup/results/$',
#        'book_lookup_results', name='mybook_lookup_results'),
#    url(r'^(?P<bookstore_id>\d+)/(?P<book_id>\d+)/pricesearch/$', 
#        'pricesearch', name='pricesearch'),
#    url(r'^seller/pricesearch/(?P<book_pk>\d+)/$',
#        'pricesearch_json', name='pricesearch_json'),
    url(r'^(?P<bookstore_id>\d+)/$', 'viewbookstore'),
    url(r'^(?P<bookstore_id>\d+)/(?P<book_id>\d+)/$', 'detail'),
)
