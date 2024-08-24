from django import forms

from .models import Book, Category, Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-textarea border-red-600 border mt-1 mb-4 block w-full border-gray-300 rounded-md shadow-sm",
                }
            ),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "w-full p-2 border rounded"}
            )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "description", "image", "borrowing_price", "categories"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control-file"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "w-full p-2 border rounded"}
            )
