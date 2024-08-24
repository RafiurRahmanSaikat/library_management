from django.contrib import admin

from .models import Book, Borrowing, Category, Review

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Review)
# admin.site.register(Borrowing)


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = [
        "book",
        "user",
        "borrowed_at",
        "returned_at",
        "balance_after_borrowing",
    ]
