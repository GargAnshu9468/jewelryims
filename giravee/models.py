from stock.constants import LockerNumberChoices, InterestChoices
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import models
from decimal import Decimal
from datetime import date


class Giravee(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_amount_without_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    locker_number = models.CharField(max_length=2, choices=LockerNumberChoices.choices(), default=LockerNumberChoices.ONE.value)
    interest_type = models.CharField(max_length=10, choices=InterestChoices.choices(), default=InterestChoices.COMPOUND.value)
    start_date = models.DateField(default=date.today)
    days_since_start = models.PositiveIntegerField(default=0)
    is_cleared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_paid_amount(self):
        return sum(txn.amount for txn in self.transactions.all())

    def calculate_interest(self, end_date=None):
        principal = Decimal(str(self.amount))
        monthly_rate = Decimal(str(self.interest_rate)) / Decimal('100')

        start = self.start_date
        end = end_date or timezone.now().date()

        self.days_since_start = (end - start).days

        rd = relativedelta(end, start)
        full_months = rd.years * 12 + rd.months

        partial_days = (end - (start + relativedelta(months=full_months))).days
        days_in_partial_month = Decimal('30')

        total_interest = Decimal('0.00')
        yearly_interest_accum = Decimal('0.00')

        for m in range(full_months):
            interest = (principal * monthly_rate).quantize(Decimal('0.01'))
            total_interest += interest

            if self.interest_type == InterestChoices.COMPOUND.value:
                yearly_interest_accum += interest

                if yearly_interest_accum and (m + 1) % 12 == 0:
                    principal += yearly_interest_accum
                    yearly_interest_accum = Decimal('0.00')

        if partial_days > 0:
            partial_interest = (principal * monthly_rate * Decimal(partial_days) / days_in_partial_month).quantize(Decimal('0.01'))
            total_interest += partial_interest

        return total_interest

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        interest = self.calculate_interest()
        paid_amount = self.total_paid_amount()

        updated_due = Decimal(str(self.amount)) + interest - paid_amount
        due_amount_without_interest = updated_due - interest

        Giravee.objects.filter(pk=self.pk).update(
            due_amount_without_interest=due_amount_without_interest,
            due_amount=updated_due,
            paid_amount=paid_amount,
            interest_amount=interest,
            days_since_start=self.days_since_start
        )

        if updated_due <= 0 and not self.is_cleared:
            Giravee.objects.filter(pk=self.pk).update(is_cleared=True)

    def __str__(self):
        return self.name


class GiraveeTransaction(models.Model):
    giravee = models.ForeignKey(Giravee, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=date.today)
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.giravee.save()

    def __str__(self):
        return f"{self.giravee.name} - ₹{self.amount} on {self.date}"
