import urllib
import datetime
from xml.etree import ElementTree
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

from packages.functions import *

# Lookup Engine parent and child models
class LookupEngine(models.Model):
    bookstore = models.ForeignKey(Bookstore)

class LookupISBNDB(LookupEngine):
    engine_name = "isbndb"
    api_url = "https://isbndb.com/api/books.xml?access_key={apikey}"
    rtype = "&results={rtype}"
    stype = "&index1={stype}"
    sval = "&value1={sval}"

    # User's ISBNDB.com API access key
    api_key = models.CharField(max_length=20)

    def __unicode__(self):
        return unicode(self.engine_name)

    # assemble lookup URL according to API
    def get_dom(self, my_rtype, my_stype, my_sval):

        url = self.api_url.format(apikey=self.api_key) + 
              self.rtype.format(rtype=my_rtype) + 
              self.stype.format(stype=my_stype) + 
              self.sval.format(sval=my_sval)

        try:
            dom = ElementTree.parse(urllib.urlopen(url)) 
        except (IOError):
            return None
        else:
            return dom


# Bookstore model
class Bookstore(models.Model):
    owner = models.ForeignKey(User)
    store_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

#    isbndb_key=models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('packages.views.mybookstore_detail', 
                       args=(self.pk,))

    def __unicode__(self):
        return unicode(self.store_name)

    def get_lookup_choices(self):
        engines = self.lookupengine_set.all()
        if not engines:
            return None
        else:
            return [{'value':e.id, 'name':e.engine_name} for e in engines]

    def get_lookup_list(self, lookup_type, value):        
        if value:
            if lookup_type is 'mybooks':
                return self.get_mybooks_list(value)
            else: 
                engine = self.lookupengine_set.all().get(engine_name=lookup_type)
                if engine:
                    book = Book(bookstore=self, date_added=datetime.datetime.now(), 
                                myprice=0.0, isbn=my_isbn)
                    if book.set_data(self, engine):
                        book.shelf = 'lookup'
                        return book
                    else:
                        return None

        else:
            return self.book_set.all()

    def get_mybooks_list(self, sstr):
        mybooks_list = []
        mybooks_list = self.book_set.filter(
            Q(isbn__contains=sstr) | Q(title__contains=sstr) | Q(authors__contains=sstr)
            )
        return mybooks_list

    def get_isbndb_book(self, my_isbn):
        book = Book(bookstore=self, date_added=datetime.datetime.now(), 
                    myprice=0.0, isbn=my_isbn)
        if book.set_data(self):
            book.shelf = 'lookup'
            return book
        else:
            return None


# Book model
class Book(models.Model):

    # define choices
    SHELF_CHOICES = (
        ('public', 'Public'), ('lookup', 'Lookup'),
        ('trash', 'Trash'),   ('sold', 'Sold'), 
        )
    MEDIA_CHOICES = (
        ('NO', '----'),        ('P', 'Paperback'),
        ('H', 'Hardcover'),    ('MM', 'Mass Market PB'),
        ('CD', 'Audio CD'),    ('DVD', 'DVD'),
        ('VHS', 'VHS'),        ('VG', 'Video Game'),
        ('SC', 'Softcover'),   ('LP', 'LP Record'),
        ('12', '12in Record'), ('10', '10in Record'),
        ('7', '7in Record'),
        )
    CONDITION_CHOICES = (
        ('NO', '----'),                    ('ULN', 'Used: Like New'),
        ('UVG', 'Used: Very Good'),        ('UG', 'Used: Good'),
        ('UA', 'Used: Acceptable'),        ('CLN', 'Collectible: Like New'),
        ('CVG', 'Collectible: Very Good'), ('CG', 'Collectible: Good'),
        ('CA', 'Collectible: Acceptable'), ('NEW', 'New'),
        )

    # Bookstore is PK for the Brat
    bookstore = models.ForeignKey(Bookstore, blank=True)
    date_added = models.DateTimeField('date added', blank=True)
    sku = models.CharField(max_length=100, blank=True)
    # Primary data fields
    title = models.CharField(max_length=100, blank=True)
    title_long = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(validators=[validate_isbn], max_length=20, blank=True)
    authors = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    pub_date = models.DateTimeField('date published', blank=True)
    media = models.CharField(max_length=24, choices=MEDIA_CHOICES, default='NO')
    volume = models.CharField(max_length=24, blank=True)
    edition = models.CharField(max_length=24, blank=True)
    keywords = models.TextField(max_length=200, blank=True)
    # Secondary data fields
    condition = models.CharField(max_length=24, choices=CONDITION_CHOICES, default='NO')
    image_url = models.URLField(max_length=200, blank=True)
    summary = models.TextField(max_length=500, blank=True)
    notes = models.TextField(max_length=500, blank=True)

    # SKU is PK for Bookstore (seller)
    sku = models.CharField(max_length=100, blank=True)
    # Price fields
    myprice = models.FloatField('my price', blank=True)
    dprice = []
    # Primary filter property
    myshelf = models.CharField(max_length=12, choices=SHELF_CHOICES, default='public')

    def get_absolute_url(self):
        return reverse('packages.views.mybook_detail', 
                       args=(self.bookstore.id, self.pk,))

    def __unicode__(self):
        return unicode(self.isbn)

    # validate ISBN
    def is_valid_isbn(self):
        isbn = "".join(self.isbn.split('-'))
        self.isbn = "".join(isbn.split())
        if len(self.isbn) == 13:
            return self.is_valid_isbn13()
        elif len(self.isbn) != 10:
            return False
        else:
            isbn = self.isbn
            last = 10 if isbn[-1] in ["X", "x"] else int(isbn[-1])
            weighted = [int(num)*weight for num, weight in
                        zip(isbn[:-1], reversed(range(2, 11)))]
            return (sum(weighted) + last) %11==0

    # validate ISBN13
    def is_valid_isbn13(self):
        isbn13 = self.isbn
        total = sum([int(num)*weight for num, weight in zip(isbn13, (1,3)*6)])
        ck = 10-(total%10)
        return ck == int(isbn13[-1])


    # populate book data from ISBNDB.com
    def set_data(self, bookstore=None, engine=None):
        if not bookstore:
            if self.bookstore:
                bookstore = self.bookstore
            else:
                return False
        if not self.is_valid_isbn():
            return False
        elif engine:
            isbn = self.isbn
#            access_key = bookstore.access_key
#            dom = get_dom(access_key, "details", "isbn", isbn)
            dom = engine.set_dom(self, "details", "isbn", isbn)
            if not dom:
                return False
            else:
                for item in dom.getiterator('Title'):
                    self.title = item.text
                for item in dom.getiterator('TitleLong'):
                    if item.text:
                        self.title_long = item.text
                    else:
                        self.title_long = ""
                for item in dom.getiterator('AuthorsText'):
                    if item.text:
                        self.authors = item.text
                    else:
                        self.authors = ""
                for item in dom.getiterator('PublisherText'):
                    if item.text:
                        self.publisher = item.text
                    else:
                        self.publisher = ""
                dom = get_dom(access_key, "texts", "isbn", isbn)
                if dom:
                    for item in dom.getiterator('Summary'):
                        if item.text:
                            self.summary = item.text
                        else:
                            self.summary = ""
                    for item in dom.getiterator('Notes'):
                        if item.text:
                            self.notes = item.text
                        else:
                            self.notes = ""
                return True

    # populate price data from ISBNDB.com
    def isbn_db(self):
        tmp_dprice = []
        access_key = self.bookstore.access_key
        dom = get_dom(access_key, "prices", "isbn", self.isbn)
        if dom:
            for pr in dom.getiterator('Price'):
                tmp_dprice.append({'store': pr.get('store_id'), 
                                   'price': '{:.2f}'.format(float(pr.get('price'))),
                                   'currency_code': pr.get('currency_code'), 
                                   'is_new': pr.get('is_new'),
                                   'is_in_stock': pr.get('is_in_stock'), 
                                   'is_historic': pr.get('is_historic'),
                                   })
        self.dprice = tmp_dprice

        # computed prices
        usd_list = []
        new_list = []
        for dpr in self.dprice:
            if dpr.get('currency_code') == "USD":
                if dpr.get('is_new') not in ['1',]:
                    usd_list.append(float(dpr.get('price')))
                else:
                    new_list.append(float(dpr.get('price')))
        if usd_list:
            avg_usd_dprice = float(sum(usd_list) / len(usd_list))
            self.dprice.extend([
                    {'store': "Average Used Price", 
                     'price': '{:.2f}'.format(avg_usd_dprice),
                     'is_new': '0',},
                    {'store': "Low Used Price", 
                     'price': '{:.2f}'.format(min(usd_list)), 
                     'is_new': '0',},
                    {'store': "High Used Price", 
                     'price': '{:.2f}'.format(max(usd_list)), 
                     'is_new': '0',},
                    ])

        if new_list:
            avg_new_dprice = float(sum(new_list) / len(new_list))
            self.dprice.extend([
                    {'store': "Average New Price", 
                     'price': '{:.2f}'.format(avg_new_dprice), 
                     'is_new': '1',},
                    {'store': "Low New Price", 
                     'price': '{:.2f}'.format(min(new_list)),
                     'is_new': '1',},
                    {'store': "High New Price", 
                     'price': '{:.2f}'.format(max(new_list)),
                     'is_new': '1',},
                    ])

