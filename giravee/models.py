from dateutil.relativedelta import relativedelta
from stock.constants import LockerNumberChoices
from django.utils import timezone
from calendar import monthrange
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
    locker_number = models.CharField(max_length=2, choices=LockerNumberChoices.choices(), default='1')
    start_date = models.DateField(default=date.today)
    is_cleared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_paid_amount(self):
        return sum(txn.amount for txn in self.transactions.all())

    def _month_interest(self, principal, monthly_rate, days_fraction=1):
        """Calculate interest for a month or fraction of month."""
        return (principal * monthly_rate * Decimal(str(days_fraction))).quantize(Decimal('0.01'))

    def calculate_interest(self, end_date=None):
        principal = Decimal(str(self.amount))

        rate = Decimal(str(self.interest_rate)) / Decimal('100')
        monthly_rate = rate / Decimal('12')

        start = self.start_date
        end = end_date or timezone.now().date()

        transactions = list(self.transactions.order_by('date'))
        current = start

        total_interest = Decimal('0.00')

        while current < end:
            month_days = monthrange(current.year, current.month)[1]
            month_end = current.replace(day=month_days)

            if end <= month_end:
                days_fraction = Decimal((end - current).days) / Decimal(month_days)

            else:
                days_fraction = Decimal((month_end - current).days + 1) / Decimal(month_days)

            interest = self._month_interest(principal, monthly_rate, days_fraction)
            total_interest += interest
            principal += interest

            period_end = min(month_end + relativedelta(days=1), end)
            period_txns = [t for t in transactions if current <= t.date < period_end]

            for txn in period_txns:
                principal = max(principal - txn.amount, Decimal('0'))

            current = period_end

        return total_interest

    def total_due(self):
        return Decimal(str(self.amount)) + self.calculate_interest() - self.total_paid_amount()

    def interest_history(self, end_date=None):
        principal = Decimal(str(self.amount))

        rate = Decimal(str(self.interest_rate)) / Decimal('100')
        monthly_rate = rate / Decimal('12')

        history = []

        start = self.start_date
        end = end_date or timezone.now().date()

        transactions = self.transactions.order_by('date')
        current = start

        total_interest = Decimal('0.00')

        while current < end:
            month_days = monthrange(current.year, current.month)[1]
            month_end = current.replace(day=month_days)

            if end <= month_end:
                days_fraction = Decimal((end - current).days) / Decimal(month_days)

            else:
                days_fraction = Decimal((month_end - current).days + 1) / Decimal(month_days)

            interest = self._month_interest(principal, monthly_rate, days_fraction)
            total_interest += interest
            principal += interest

            period_end = min(month_end + relativedelta(days=1), end)
            period_txns = [t for t in transactions if current <= t.date < period_end]

            total_paid_this_period = Decimal('0.00')

            for txn in period_txns:
                principal = max(principal - txn.amount, Decimal('0'))
                total_paid_this_period += txn.amount

            history.append({
                'from': current,
                'to': period_end,
                'interest': interest,
                'paid': total_paid_this_period if total_paid_this_period > 0 else None,
                'remaining_principal': principal
            })

            current = period_end

        return {
            'history': history,
            'total_interest': total_interest
        }

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
            interest_amount=interest
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
