# Admin interface

from packages.models import Book
from django.contrib import admin

class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Book Information', {'fields': ['title', 'isbn']}),
        ('Inventory Information', {'fields': ['myprice', 'date_added']}),
    ]
    list_display = ('title', 'isbn')
    search_fields = ['title', 'isbn']

admin.site.register(Book, BookAdmin)
