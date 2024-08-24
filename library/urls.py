from django.urls import path

from . import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    path("add_book", views.AddBookView.as_view(), name="add_book"),
    path("add_category", views.AddCategoryView.as_view(), name="add_category"),
    path("books/<int:pk>/return/", views.ReturnBookView.as_view(), name="return_book"),
    path(
        "reviews/create/<int:pk>/",
        views.ReviewCreateView.as_view(),
        name="review_create",
    ),
    path(
        "books/<int:pk>/borrow/",
        views.BorrowBookView.as_view(),
        name="borrow_book",
    ),
    path(
        "books/<int:pk>/return/",
        views.ReturnBookView.as_view(),
        name="return_book",
    ),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("deposit/", views.DepositView.as_view(), name="deposit"),
]
