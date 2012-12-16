# packages/tables.py
import django_tables2 as tables
from django_tables2.utils import A #accessor
from packages.models import Book

class BookTable(tables.Table):
    act = tables.CheckBoxColumn(accessor='pk')
    title = tables.LinkColumn('book_update', args=[A('bookstore_id'),A('pk')])

    class Meta:
        model = Book
        exclude = ("id","owner","isbn","bookstore","date_added",
                   "title_long","summary","notes", )
        attrs = {"class": "paleblue"}
        empty_text = "No books listed."
