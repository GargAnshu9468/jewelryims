from stock.constants import DiscountChoices, PaymentMethodChoices, LabourOrMakingChargeChoices
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from stock.models import Stock
from django.db import models
from decimal import Decimal
from datetime import date


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PurchaseBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchasesupplier")
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethodChoices.choices(),
        default=PaymentMethodChoices.CASH.value,
        blank=True,
        null=True
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DiscountChoices.choices(),
        default=DiscountChoices.NONE.value,
        blank=True,
        null=True
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_note = models.TextField(blank=True, null=True)
    labour_making_charge_note = models.TextField(blank=True, null=True)
    labour_making_charge_type = models.CharField(
        max_length=20,
        choices=LabourOrMakingChargeChoices.choices(),
        default=LabourOrMakingChargeChoices.NONE.value,
        blank=True,
        null=True
    )
    labour_making_charge_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Bill no: {str(self.billno)}"

    def get_items_list(self):
        return PurchaseItem.objects.filter(billno=self)

    def get_total_price(self):
        purchaseitems = self.get_items_list()
        total = sum(item.totalprice for item in purchaseitems)

        # Apply Discount

        if self.discount_type and self.discount_value:
            if self.discount_type == 'Fixed':
                total -= self.discount_value

            elif self.discount_type == 'Percentage':
                total -= (total * self.discount_value / Decimal('100'))

        # Apply Labour/Making Charge

        if self.labour_making_charge_type and self.labour_making_charge_value:
            if self.labour_making_charge_type == 'Fixed':
                total += self.labour_making_charge_value

            elif self.labour_making_charge_type == 'Per Gram':
                total_weight = sum(item.weight or 0 for item in purchaseitems)
                total += total_weight * self.labour_making_charge_value

        return total


class PurchaseItem(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name="purchasebillno")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="purchaseitem")
    stock_note = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill no: {self.billno.billno}, Item = {self.stock.name}"


class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name="purchasedetailsbillno")
    gst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_after_discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_labour_making_charge = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_weight = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Bill no: {str(self.billno.billno)}"


@receiver(post_save, sender=PurchaseBillDetails)
def update_purchase_bill_details(sender, instance, **kwargs):
    bill = instance.billno

    # Step 1: Get total of all PurchaseItem totalprices
    items_total = bill.purchasebillno.aggregate(total=Sum('totalprice'))['total'] or Decimal('0.00')

    # Step 2: Apply discount before GST
    discount_type = bill.discount_type
    discount_value = Decimal(bill.discount_value or '0.00')

    if discount_type == 'Fixed':
        total_discount = discount_value

    elif discount_type == 'Percentage':
        total_discount = (items_total * discount_value) / Decimal('100')

    else:
        total_discount = Decimal('0.00')

    discounted_total = items_total - total_discount

    # Step 3: Calculate total_labour_making_charge on discounted_total

    labour_making_charge_type = bill.labour_making_charge_type
    labour_making_charge_value = Decimal(bill.labour_making_charge_value or '0.00')

    total_weight = sum(item.weight or 0 for item in bill.purchasebillno.all())

    if labour_making_charge_type == 'Fixed':
        total_labour_making_charge = labour_making_charge_value

    elif labour_making_charge_type == 'Per Gram':
        total_labour_making_charge = labour_making_charge_value * total_weight

    else:
        total_labour_making_charge = Decimal('0.00')

    # Step 4: final_subtotal = discounted_total + total_labour_making_charge

    final_subtotal = discounted_total + total_labour_making_charge

    # Step 5: Now, calculate GST on final_subtotal
    gst_percent = Decimal(instance.gst or '0.00')
    gst_amount = (final_subtotal * gst_percent) / Decimal('100')

    # Step 5: total = items_total + gst_amount + total_labour_making_charge
    total = items_total + gst_amount + total_labour_making_charge

    # Step 6: total_after_discount = final_subtotal + gst_amount
    total_after_discount = final_subtotal + gst_amount

    # Step 7: Update PurchaseBillDetails
    PurchaseBillDetails.objects.filter(pk=instance.pk).update(
        total=total,
        total_after_discount=total_after_discount,
        total_discount=total_discount,
        gst_amount=gst_amount,
        total_labour_making_charge=total_labour_making_charge,
        total_weight=total_weight
    )

    # Step 8: Update PurchaseBill
    payment = Decimal(bill.payment_amount or '0.00')
    remaining = total_after_discount - payment

    bill.remaining_amount = max(remaining, Decimal('0.00'))
    bill.save(update_fields=['remaining_amount'])


class SaleBill(models.Model):
    billno = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="salebills")
    payment_method = models.CharField(
        max_length=50,
        choices=PaymentMethodChoices.choices(),
        default=PaymentMethodChoices.CASH.value,
        blank=True,
        null=True
    )
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_type = models.CharField(
        max_length=10,
        choices=DiscountChoices.choices(),
        default=DiscountChoices.NONE.value,
        blank=True,
        null=True
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_note = models.TextField(blank=True, null=True)
    labour_making_charge_note = models.TextField(blank=True, null=True)
    labour_making_charge_type = models.CharField(
        max_length=20,
        choices=LabourOrMakingChargeChoices.choices(),
        default=LabourOrMakingChargeChoices.NONE.value,
        blank=True,
        null=True
    )
    labour_making_charge_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Bill no: {str(self.billno)}"

    def get_items_list(self):
        return SaleItem.objects.filter(billno=self)

    def get_total_price(self):
        saleitems = self.get_items_list()
        total = sum(item.totalprice for item in saleitems)

        # Apply Discount

        if self.discount_type and self.discount_value:
            if self.discount_type == 'Fixed':
                total -= self.discount_value

            elif self.discount_type == 'Percentage':
                total -= (total * self.discount_value / Decimal('100'))

        # Apply Labour/Making Charge

        if self.labour_making_charge_type and self.labour_making_charge_value:
            if self.labour_making_charge_type == 'Fixed':
                total += self.labour_making_charge_value

            elif self.labour_making_charge_type == 'Per Gram':
                total_weight = sum(item.weight or 0 for item in saleitems)
                total += total_weight * self.labour_making_charge_value

        return total


class SaleItem(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name="salebillno")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="saleitem")
    stock_note = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bill no: {self.billno.billno}, Item = {self.stock.name}"


class SaleBillDetails(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name="saledetailsbillno")
    gst = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_after_discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_labour_making_charge = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_weight = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Bill no: {str(self.billno.billno)}"


@receiver(post_save, sender=SaleBillDetails)
def update_sale_bill_details(sender, instance, **kwargs):
    bill = instance.billno

    # Step 1: Get total of all SaleItem totalprices
    items_total = bill.salebillno.aggregate(total=Sum('totalprice'))['total'] or Decimal('0.00')

    # Step 2: Apply discount BEFORE tax
    discount_type = bill.discount_type
    discount_value = Decimal(bill.discount_value or '0.00')

    if discount_type == 'Fixed':
        total_discount = discount_value

    elif discount_type == 'Percentage':
        total_discount = (items_total * discount_value) / Decimal('100')

    else:
        total_discount = Decimal('0.00')

    discounted_total = items_total - total_discount

    # Step 3: Calculate total_labour_making_charge on discounted_total

    labour_making_charge_type = bill.labour_making_charge_type
    labour_making_charge_value = Decimal(bill.labour_making_charge_value or '0.00')

    total_weight = sum(item.weight or 0 for item in bill.salebillno.all())

    if labour_making_charge_type == 'Fixed':
        total_labour_making_charge = labour_making_charge_value

    elif labour_making_charge_type == 'Per Gram':
        total_labour_making_charge = labour_making_charge_value * total_weight

    else:
        total_labour_making_charge = Decimal('0.00')

    # Step 4: final_subtotal = discounted_total + total_labour_making_charge

    final_subtotal = discounted_total + total_labour_making_charge

    # Step 5: Now, calculate GST on final_subtotal
    gst_percent = Decimal(instance.gst or '0.00')
    gst_amount = (final_subtotal * gst_percent) / Decimal('100')

    # Step 5: total = items_total + gst_amount + total_labour_making_charge
    total = items_total + gst_amount + total_labour_making_charge

    # Step 6: total_after_discount = final_subtotal + gst_amount
    total_after_discount = final_subtotal + gst_amount

    # Step 6: Update SaleBillDetails
    SaleBillDetails.objects.filter(pk=instance.pk).update(
        total=total,
        total_after_discount=total_after_discount,
        total_discount=total_discount,
        gst_amount=gst_amount,
        total_labour_making_charge=total_labour_making_charge,
        total_weight=total_weight
    )

    # Step 7: Update remaining in SaleBill
    payment = Decimal(bill.payment_amount or '0.00')
    remaining = total_after_discount - payment

    bill.remaining_amount = max(remaining, Decimal('0.00'))
    bill.save(update_fields=['remaining_amount'])


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer name: {str(self.name)}"
