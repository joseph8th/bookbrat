from django import forms
from packages.models import Bookstore, Book

# UserProfileForm removed from this ver. 0.1 #

class BookstoreForm(forms.ModelForm):
    class Meta:
        model = Bookstore
        exclude = ('owner')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ('bookstore', 'dprice')
