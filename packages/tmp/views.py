# Joseph Edwards - joseph8th@urcomics.com
# BookBrat Bookstore Inventory management system.
# Version 0.1 - Very alpha. 1st deployed version.

import datetime

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django_tables2 import RequestConfig

from packages.functions import *
from packages.models import Bookstore, Book
from packages.forms import BookstoreForm, BookForm
from packages.tables import BookTable

from accounts.models import UserProfile

#### temp globals ####
ACTION_LIST = [{'value':'delete', 'name':'Delete'},]

#### Account views ####

@login_required
def myaccount(request):
    owner = request.user
    return render_to_response('accounts/myaccount.html',
                              context_instance=RequestContext(request))

### Public views ####

def viewbookstore(request, bookstore_id):
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    latest_book_list = bookstore.book_set.all().order_by('id')[:]
    return render_to_response('packages/booklist.html', 
                              {'bookstore': bookstore, 
                               'latest_book_list': latest_book_list},
                              context_instance=RequestContext(request))     


def detail(request, bookstore_id, book_id):
    bs = get_object_or_404(Bookstore, pk=bookstore_id)
    b = bs.book_set.get(pk=book_id)
    return HttpResponseRedirect(reverse('packages.views.results', 
                                            args=(bs.id, b.id,)))


def results(request, bookstore_id, book_id):
    bs = get_object_or_404(Bookstore, pk=bookstore_id)
    b = bs.book_set.get(pk=book_id)
    return render_to_response('packages/results.html', 
                              {'bookstore': bs, 'book': b}, 
                              context_instance=RequestContext(request))


#### User store-centric views ####

class BookstoreCreate(CreateView):
    form_class = BookstoreForm
    model = Bookstore

class BookstoreUpdate(UpdateView):
    form_class = BookstoreForm
    model = Bookstore

class BookstoreDelete(DeleteView):
    model = Bookstore
    success_url = reverse_lazy('mybookstores')

@login_required
def mybookstores(request):
    owner = request.user
    bookstore_list = owner.bookstore_set.all().order_by('id')[:]
    return render_to_response('packages/mybookstores.html', 
                              {'bookstore_list': bookstore_list},
                              context_instance=RequestContext(request))

@login_required
def mybookstore_detail(request, bookstore_id): 
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    table = BookTable(bookstore.book_set.all())
    RequestConfig(request).configure(table)
    return render_to_response('packages/mybs_detail.html', 
                              {'bookstore': bookstore, 
                               'table': table,
                               'act_list': ACTION_LIST},
                              context_instance=RequestContext(request))     

#### Book-centric User views ####

class BookCreate(CreateView):
    form_class = BookForm
    model = Book

class BookUpdate(UpdateView):
    form_class = BookForm
    model = Book

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BookUpdate, self).dispatch(*args, **kwargs)

class BookDelete(DeleteView):
    model = Book

    def get_success_url(self, **kwargs):
        return reverse('bookstore_detail', args=(self.bookstore_id,))

    def delete(self, request, *args, **kwargs):
        self.bookstore_id = self.get_object().bookstore.id
        return super(BookDelete, self).delete(request, *args, **kwargs)

@login_required
def mybooks_action(request, bookstore_id):
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    if request.method == 'POST':
        pks = request.POST.getlist("act")
        mybooks = bookstore.book_set.filter(pk__in=pks)
        if request.POST['action'] == 'delete':
            for book in mybooks:
                book.myshelf = 'trash'
                book.save()
    return HttpResponseRedirect(reverse('bookstore_detail', args=(bookstore.id,)))
        

@login_required
def book_lookup(request, bookstore_id):
    owner = request.user
    bookstore = owner.bookstore_set.all().get(pk=bookstore_id)
    if request.method == 'POST':
        wrk_isbn = request.POST['isbn']
        if wrk_isbn != "":
            book = bookstore.book_set.create(owner=owner, isbn=wrk_isbn, myprice=0.0,
                                             date_added=datetime.datetime.now())
            if bookstore.set_data(book):
                book.shelf = 'lookup'
                book.save()
                return HttpResponseRedirect(reverse('mybook_lookup_results',
                                                    args=(bookstore.id, book.id,)))
            else:
                book.delete()        
        latest_book_list = bookstore.book_set.all().order_by('-date_added')[:]
        message = "Invalid ISBN. No book found."
        return render_to_response('packages/mybs_detail.html', 
                                  {'bookstore': bookstore, 
                                   'latest_book_list': latest_book_list},
                                  context_instance=RequestContext(request))            

@login_required
def book_lookup_results(request, bookstore_id, book_id):
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    book = bookstore.book_set.get(pk=book_id)
    bookstore.isbn_db(book)
    if request.method == 'POST':
        if request.POST['add'] == "True":
            book.shelf = 'public'
            book.save()
            return HttpResponseRedirect(reverse('mybook_detail', 
                                                args=(bookstore.id, book.id,)))
        else:
            book.delete()
            latest_book_list = bookstore.book_set.all().order_by('-date_added')[:]
            return render_to_response('packages/mybs_detail.html', 
                                      {'bookstore': bookstore, 
                                       'latest_book_list': latest_book_list},
                                      context_instance=RequestContext(request))            
    return render_to_response('packages/mybook_lookup_results.html',
                              {'bookstore': bookstore, 'book': book},
                              context_instance=RequestContext(request))


@login_required
def mybook_detail(request, bookstore_id, book_id):
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    book = bookstore.book_set.get(pk=book_id)
    return render_to_response('packages/mybook_detail.html', 
                              {'bookstore' : bookstore, 'book': book}, 
                              context_instance=RequestContext(request))


@login_required
def pricesearch(request, bookstore_id, book_id):
    bs = get_object_or_404(Bookstore, pk=bookstore_id)
    b = bs.book_set.get(pk=book_id)
    bs.isbn_db(b)
    message = "Set a price."
    if 'price' in request.POST:
        b.myprice = request.POST['price']
        b.dprice = []
        b.save()
        message = "Price set."
    return render_to_response('packages/mybook_detail.html', 
                              {'bookstore' : bs, 'book': b,
                               'message': message}, 
                              context_instance=RequestContext(request))

@login_required
def pricesearch_json(request, book_pk):
    msg = {"price_list":[]}
    if request.is_ajax():
        book = get_object_or_404(Book, pk=book_pk)
        book.bookstore.isbn_db(book)
        msg['price_list'] = "<ul>"
        for p in book.dprice:
            msg['price_list'] = msg['price_list']+"<li>"+ \
                p['store']+": $"+p['price']+" "+"</li>"
        msg['price_list'] = msg['price_list']+"</ul>"
    else:
        msg = "AJAX not working here."
    json = simplejson.dumps(msg)
    return HttpResponse(json, mimetype='application/json')
