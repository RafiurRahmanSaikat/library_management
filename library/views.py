from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from accounts.models import UserAccount

from .forms import BookForm, CategoryForm, ReviewForm
from .models import Book, Borrowing, Category, Review


def send_transaction_email(user, amount, subject, template):
    message = render_to_string(
        template,
        {
            "user": user,
            "amount": amount,
        },
    )
    send_email = EmailMultiAlternatives(subject, "", to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class BookListView(ListView):
    model = Book
    template_name = "book/book_list.html"
    context_object_name = "books"

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(categories__name=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class AddCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "book/create.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "category"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)


class AddBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "book/create.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "book"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "book/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        user_account = UserAccount.objects.filter(user=self.request.user).first()
        if user_account:
            user_has_borrowed = Borrowing.objects.filter(
                book=book, user=user_account, returned_at__isnull=True
            ).exists()
        else:
            user_has_borrowed = False
        context["user_has_borrowed"] = user_has_borrowed
        return context


class ReturnBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        borrowing = get_object_or_404(Borrowing, pk=pk, user=request.user.account)
        book = borrowing.book
        user_account = UserAccount.objects.get(user=request.user)

        borrowing.returned_at = timezone.now()
        borrowing.save()

        borrowing_price = Decimal(book.borrowing_price)
        user_account.balance += borrowing_price
        user_account.save()

        book.is_borrowed = False
        book.save()

        send_transaction_email(
            self.request.user,
            book,
            "Book Returned",
            "book/book_return_email.html",
        )

        return redirect("profile")


class BorrowBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        user_account = get_object_or_404(UserAccount, user=request.user)

        if book.is_borrowed:
            return redirect("book_detail", pk=book.pk)

        borrowing_price = Decimal(book.borrowing_price)

        if user_account.balance >= borrowing_price:
            user_account.balance -= borrowing_price
            user_account.save()

            Borrowing.objects.create(
                book=book,
                user=user_account,
                balance_after_borrowing=user_account.balance,
            )

            book.is_borrowed = True
            book.save()

            send_transaction_email(
                self.request.user,
                book,
                "Borrowed Book",
                "book/book_borrow_email.html",
            )

            return redirect("book_detail", pk=book.pk)
        else:
            return redirect("deposit")


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "book/review_create.html"
    success_url = reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk")
        return context

    def form_valid(self, form):
        form.instance.user = UserAccount.objects.get(user=self.request.user)
        form.instance.book_id = self.kwargs["pk"]
        return super().form_valid(form)


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user_account = get_object_or_404(UserAccount, user=request.user)
        borrowings = Borrowing.objects.filter(user=user_account)
        context = {
            "user_account": user_account,
            "borrowings": borrowings,
        }
        return render(request, "book/user_profile.html", context)


class DepositView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "book/deposit.html")

    def post(self, request):
        try:
            amount = Decimal(request.POST["amount"])
            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")
            user_account = UserAccount.objects.get(user=request.user)
            user_account.balance += amount
            user_account.save()

            send_transaction_email(
                self.request.user,
                amount,
                "Money Deposit",
                "book/deposit_mail.html",
            )
            return redirect("home")

        except (ValueError, InvalidOperation):
            return render(
                "book/deposit.html",
                {"error": "Invalid amount. Please enter a valid number."},
            )
