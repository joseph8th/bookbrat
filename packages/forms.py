import datetime
from django import forms

from packages.models import Bookstore, Book
from utils.forms import RequestModelForm

from packages.functions import *

# Field classes

class ISBNField(forms.Field):

    default_error_messages = {
        'invalid': u'Enter a valid ISBN.',
    }
    default_validators = [validate_isbn]

    def to_python(self, value):
        if not value:
            return []
        isbn_list = value.split(',')
        isbn_list = ["".join((isbn.split('-')).strip()) for isbn in isbn_list]
        return ["".join((isbn.split(' ')).strip()) for isbn in isbn_list]

    def validate(self, value):
        super(ISBNField, self).validate(value)

        for isbn in value:
            validate_isbn(isbn)

# Form classes

class BookstoreForm(forms.ModelForm):
    class Meta:
        model = Bookstore
        exclude = ('owner')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('bookstore')

    def save(self, bookstore, commit=True, *args, **kwargs):
        book = super(BookForm, self).save(commit=False, *args, **kwargs)
        book.bookstore = bookstore
        if commit:
            book.date_added = datetime.datetime.now()
            book.save()
        return book

class RequestBookstoreForm(RequestModelForm):
    class Meta:
        model = Bookstore
        exclude = ('owner')

    def clean(self):
        cleaned_data = super(RequestBookstoreForm, self).clean()
        if not cleaned_data.get('owner'):
            self.instance.owner = self.request.user
        return super(RequestBookstoreForm, self).clean()
