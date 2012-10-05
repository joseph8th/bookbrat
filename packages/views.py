# Joseph Edwards - joseph8th@urcomics.com
# BookBrat Bookstore Inventory management system.
# Version 0.1 - Very alpha. 1st deployed version.

import datetime

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from packages.functions import *
from packages.models import Bookstore, Book
from packages.forms import BookstoreForm, BookForm

from accounts.models import UserProfile

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

#### User store-centric views ####

#@login_required
class BookstoreCreate(CreateView):
    model = Bookstore

#@login_required
class BookstoreUpdate(UpdateView):
    model = Bookstore

#@login_required
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
    latest_book_list = bookstore.book_set.all().order_by('id')[:]
    return render_to_response('packages/mybs_detail.html', 
                              {'bookstore': bookstore, 
                               'latest_book_list': latest_book_list},
                              context_instance=RequestContext(request))     

#### Book-centric User views ####

@login_required
def book_lookup(request, bookstore_id):
    if request.method == 'POST':
        owner = request.user
        bookstore = owner.bookstore_set.all().get(pk=bookstore_id)
        wrk_isbn = request.POST['isbn']
        if wrk_isbn != "":
            book = bookstore.book_set.create(isbn=wrk_isbn, myprice=0.0,
                                             date_added=datetime.datetime.now())
            if book.set_data():
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
    book.isbn_db()
    return render_to_response('packages/mybook_lookup_results.html', 
                              {'bookstore': bookstore, 'book': book}, 
                              context_instance=RequestContext(request))

@login_required
def addbook(request, bookstore_id):
    if request.method == 'POST':
        owner = request.user
        bookstore = owner.bookstore_set.all().get(pk=bookstore_id)
        new_isbn = request.POST['isbn']
        if new_isbn != "":
            book = bookstore.book_set.create(isbn=new_isbn, myprice=0.0, 
                                             date_added=datetime.datetime.now())
            if book.set_data():
                book.save()
                return HttpResponseRedirect(reverse('packages.views.results', 
                                                    args=(bookstore.id, book.id,)))
            else:
                book.delete()        
        latest_book_list = bookstore.book_set.all().order_by('-date_added')[:]
        message = "Invalid ISBN. No book added."
        return render_to_response('packages/booklist.html', 
                                  {'bookstore': bookstore, 
                                   'latest_book_list': latest_book_list},
                                  context_instance=RequestContext(request))

@login_required
def deletebook(request, bookstore_id):
    if request.method == 'POST':
        bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
        try:
            del_id = request.POST['book']
        except (KeyError):
            latest_book_list = bookstore.book_set.all().order_by('-date_added')[:]
            error_message = "No book selected."
            return render_to_response('packages/mybs_detail.html', 
                                      {'bookstore': bookstore, 
                                       'latest_book_list': latest_book_list},
                                      context_instance=RequestContext(request))
        else:
            book = bookstore.book_set.get(pk=del_id)
            book.delete()
            latest_book_list = bookstore.book_set.all().order_by('-date_added')[:]
            return HttpResponseRedirect(reverse('bookstore_detail', 
                                                args=(bookstore.id,)))

@login_required
def mybook_detail(request, bookstore_id, book_id):
    bookstore = get_object_or_404(Bookstore, pk=bookstore_id)
    book = bookstore.book_set.get(pk=book_id)
    book.isbn_db()
    try:
        book.myprice = request.POST['price']
    except (KeyError):
        return render_to_response('packages/mybook_detail.html', 
                                  {'bookstore' : bookstore, 'book': book,
                                   'message': "Select a price."}, 
                                  context_instance=RequestContext(request))
    else:
        book.save()
        return HttpResponseRedirect(reverse('packages.views.results', 
                                            args=(bookstore.id, book.id,)))

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

@login_required
def pricesearch(request, bookstore_id, book_id):
    bs = get_object_or_404(Bookstore, pk=bookstore_id)
    b = bs.book_set.get(pk=book_id)
    try:
        b.myprice = request.POST['price']
    except (KeyError):
        b.isbn_db()
        return render_to_response('packages/detail.html', 
                                  {'bookstore' : bs, 'book': b,
                                   'message': "Select a price."}, 
                                  context_instance=RequestContext(request))
    else:
        b.save()
        return HttpResponseRedirect(reverse('packages.views.results', 
                                            args=(bs.id, b.id,)))
