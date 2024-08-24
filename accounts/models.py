from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class UserAccount(models.Model):
    user = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    account_number = models.IntegerField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=(
            ("Male", "male"),
            ("Female", "female"),
        ),
    )
    initial_amount = models.IntegerField(default=0)
    balance = models.DecimalField(
        default=Decimal("0.00"), max_digits=12, decimal_places=2
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.account_number}"
