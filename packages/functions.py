from django.core.exceptions import ValidationError
from xml.etree import ElementTree
import urllib

# Global book functions

# validate ISBN
def validate_isbn(isbn):
    isbn = "".join(isbn.split('-'))
    isbn = "".join(isbn.split())
    if len(isbn) == 13:
        total = sum([int(num)*weight for num, weight in zip(isbn, (1,3)*6)])
        ck = 10-(total%10)
        if not ck == int(isbn[-1]):
            raise ValidationError(u'%s is not a valid ISBN.' % isbn)
    elif len(isbn) != 10:
        raise ValidationError(u'%s is not a valid ISBN.' % isbn)
    else:
        last = 10 if isbn[-1] in ["X", "x"] else int(isbn[-1])
        weighted = [int(num)*weight for num, weight in
                    zip(isbn[:-1], reversed(range(2, 11)))]
        if not (sum(weighted) + last) %11==0:
            raise ValidationError(u'%s is not a valid ISBN.' % isbn)


# validate ISBN13
def is_valid_isbn13(isbn13):
    total = sum([int(num)*weight for num, weight in zip(isbn13, (1,3)*6)])
    ck = 10-(total%10)
    if not ck == int(isbn13[-1]):
        raise ValidationError(u'%s is not a valid ISBN.' % isbn)


# assemble lookup URL according to API
def get_dom(my_apikey, my_rtype, my_stype, my_sval):

    # Temp lookup URL config
    ISBN_DB = "https://isbndb.com/api/books.xml?access_key={apikey}"
    RTYPE = "&results={rtype}"
    STYPE = "&index1={stype}"
    SVAL = "&value1={sval}"

    url = ISBN_DB.format(apikey=my_apikey) + RTYPE.format(rtype=my_rtype) + STYPE.format(stype=my_stype) + SVAL.format(sval=my_sval)
    try:
        dom = ElementTree.parse(urllib.urlopen(url)) 
    except (IOError):
        return None
    else:
        return dom


# populate book data from ISBNDB.com
def set_data(bookstore, book):
    if not is_valid_isbn(book.isbn):
        return False
    else:
        dom = get_dom(bookstore.access_key, "details", "isbn", book.isbn)
        if not dom:
            return False
        else:
            for item in dom.getiterator('Title'):
                book.title = item.text
            for item in dom.getiterator('TitleLong'):
                if item.text:
                    book.title_long = item.text
                else:
                    book.title_long = ""
            for item in dom.getiterator('AuthorsText'):
                if item.text:
                    book.authors = item.text
                else:
                    book.authors = ""
            for item in dom.getiterator('PublisherText'):
                if item.text:
                    book.publisher = item.text
                else:
                    book.publisher = ""
            dom = get_dom(book.bookstore.access_key, "texts", "isbn", book.isbn)
            if dom:
                for item in dom.getiterator('Summary'):
                    if item.text:
                        book.summary = item.text
                    else:
                        book.summary = ""
                for item in dom.getiterator('Notes'):
                    if item.text:
                        book.notes = item.text
                    else:
                        book.notes = ""
            return True

# populate price data from ISBNDB.com
def isbn_db(bookstore, book):
    tmp_dprice = []
    dom = get_dom(bookstore.access_key, "prices", "isbn", book.isbn)
    if dom:
        for pr in dom.getiterator('Price'):
            tmp_dprice.append({'store': pr.get('store_id'), 
                               'price': '{:.2f}'.format(float(pr.get('price'))),
                               'currency_code': pr.get('currency_code'), 
                               'is_new': pr.get('is_new'),
                               'is_in_stock': pr.get('is_in_stock'), 
                               'is_historic': pr.get('is_historic'),
                               })
    book.dprice = tmp_dprice
    usd_list = []
    for dpr in book.dprice:
        if dpr.get('currency_code') == "USD":
            usd_list.append(float(dpr.get('price')))
    avg_dprice = float(sum(usd_list) / len(usd_list))
    book.dprice.append({'store': "mean", 'price': '{:.2f}'.format(avg_dprice),})
