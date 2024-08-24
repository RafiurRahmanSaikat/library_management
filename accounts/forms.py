from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import UserAccount


class UserRegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(
        choices=(
            ("Male", "male"),
            ("Female", "female"),
        )
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "date_of_birth",
            "gender",
        ]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "This username is already taken. Please choose a different one."
            )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserAccount.objects.create(
                user=user,
                account_number=1000 + user.id,
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                gender=self.cleaned_data.get("gender"),
                initial_amount=0,
            )
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("usable_password")
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "w-full p-2 border rounded"}
            )


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": "w-full p-2 border rounded bg-gray-100",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "w-full p-2 border rounded",
            }
        )


class UserUpdateForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(
        choices=(
            ("Male", "male"),
            ("Female", "female"),
        ),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "gender",
            "date_of_birth",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:

            self.fields[field].widget.attrs.update(
                {
                    "class": "appearance-none block w-full bg-gray-200 "
                    "text-gray-700 border border-gray-200 rounded "
                    "py-3 px-4 leading-tight focus:outline-none "
                    "focus:bg-white focus:border-gray-500"
                }
            )
        if self.instance:
            try:
                user_account = self.instance.account
            except UserAccount.DoesNotExist:
                user_account = None

            if user_account:
                self.fields["date_of_birth"].initial = user_account.date_of_birth
                self.fields["gender"].initial = user_account.gender

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user_account, created = UserAccount.objects.get_or_create(user=user)
            user_account.date_of_birth = self.cleaned_data.get("date_of_birth")
            user_account.gender = self.cleaned_data.get("gender")
            user_account.save()

        return user
