import urllib
from xml.etree import ElementTree
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse

ISBN_DB = "https://isbndb.com/api/books.xml?access_key={apikey}"
RTYPE = "&results={rtype}"
STYPE = "&index1={stype}"
SVAL = "&value1={sval}"

# USER PROFILES removed from here this ver. 0.1 #
# see bu/apps-v0-bu/../models.py for this code #

class Bookstore(models.Model):
    owner = models.ForeignKey(User)
    store_name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    access_key = models.CharField(max_length=20)

    def get_absolute_url(self):
        return reverse('packages.views.mybookstore_detail', 
                       args=(self.pk,))

    def __unicode__(self):
        return unicode(self.store_name)

class Book(models.Model):
    bookstore = models.ForeignKey(Bookstore)
    date_added = models.DateTimeField('date added')
    # Basic data fields
    title = models.CharField(max_length=100)
    title_long = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13)
    authors = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=100, blank=True)
    # Detail fields
    summary = models.TextField(max_length=500, blank=True)
    notes = models.TextField(max_length=500, blank=True)
    # Price fields
    myprice = models.FloatField('my price')
    dprice = []

    def get_dom(self, my_apikey, my_rtype, my_stype, my_sval):
        url = ISBN_DB.format(apikey=my_apikey) + RTYPE.format(rtype=my_rtype) + STYPE.format(stype=my_stype) + SVAL.format(sval=my_sval)
        try:
            dom = ElementTree.parse(urllib.urlopen(url)) 
        except (IOError):
            return None
        else:
            return dom

    def set_data(self):
        if not self.is_valid_isbn():
            return False
        else:
            dom = self.get_dom(self.bookstore.access_key, "details", "isbn", self.isbn)
            if dom:
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
                dom = self.get_dom(self.bookstore.access_key, "texts", "isbn", self.isbn)
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

    def isbn_db(self):
        tmp_dprice = []
        dom = self.get_dom(self.bookstore.access_key, "prices", "isbn", self.isbn)
        if dom:
            for pr in dom.getiterator('Price'):
                tmp_dprice.append({'store': pr.get('store_id'), 'price': '{:.2f}'.format(float(pr.get('price'))),
                                   'currency_code': pr.get('currency_code'), 'is_new': pr.get('is_new'),
                                   'is_in_stock': pr.get('is_in_stock'), 'is_historic': pr.get('is_historic'),
                                   })
        self.dprice = tmp_dprice
        usd_list = []
        for dpr in self.dprice:
            if dpr.get('currency_code') == "USD":
                usd_list.append(float(dpr.get('price')))
        avg_dprice = float(sum(usd_list) / len(usd_list))
        self.dprice.append({'store': "mean", 'price': '{:.2f}'.format(avg_dprice),})

    def is_valid_isbn(self):
        isbn = self.isbn
        if len(isbn) == 13:
            return self.is_valid_isbn13()
        elif len(isbn) != 10:
            return False
        else:
            last = 10 if isbn[-1] in ["X", "x"] else int(isbn[-1])
            weighted = [int(num)*weight for num, weight in
                        zip(isbn[:-1], reversed(range(2, 11)))]
            return (sum(weighted) + last) %11==0

    def is_valid_isbn13(self):
        isbn13 = self.isbn
        total = sum([int(num)*weight for num, weight in zip(isbn13, (1,3)*6)])
        ck = 10-(total%10)
        return ck == int(isbn13[-1])

    def __unicode__(self):
        return unicode(self.isbn)
