from .models import Stock, Supplier, PurchaseItem, PurchaseBill, SaleItem, SaleBill, PurchaseBillDetails, SaleBillDetails, Customer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from decimal import Decimal


@login_required
def suppliers(request):

    suppliers_list = list(Supplier.objects.filter(is_deleted=False).order_by('-updated_at'))

    paginator = Paginator(suppliers_list, 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Transactions', 'url': ''},
        {'label': 'Suppliers', 'url': '/transactions/suppliers/'}
    ]

    context = {
        'pagination': pagination,
        'page_title': 'Suppliers',
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'transactions/suppliers.html', context)


@login_required
@require_POST
def get_suppliers(request):
    suppliers_list = Supplier.objects.filter(is_deleted=False).values('id', 'name', 'phone', 'address', 'email', 'gstin')
    return JsonResponse({'suppliers': list(suppliers_list)})


@login_required
@require_POST
def new_supplier(request):

    attr_dict = request.POST.dict()

    try:
        Supplier.objects.create(**attr_dict)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error adding supplier: {str(e)}'}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Supplier added successfully'})


@login_required
@require_POST
def edit_supplier(request):

    supplier_id = request.POST.get('id')
    supplier_name = request.POST.get('name')
    supplier_phone = request.POST.get('phone')
    supplier_email = request.POST.get('email')
    supplier_gstin = request.POST.get('gstin')
    supplier_address = request.POST.get('address')

    try:
        supplier = Supplier.objects.get(pk=supplier_id)

        if supplier_name:
            supplier.name = supplier_name

        if supplier_phone:
            supplier.phone = supplier_phone

        if supplier_email:
            supplier.email = supplier_email

        if supplier_gstin:
            supplier.gstin = supplier_gstin

        if supplier_address:
            supplier.address = supplier_address

        supplier.save()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supplier with the provided ID does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Supplier updated successfully.'})


@login_required
@require_POST
def delete_supplier(request):

    supplier_id = request.POST.get('id')

    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supplier with the provided ID does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Supplier deleted successfully.'})


@login_required
@require_POST
def supplier_details(request):

    supplier_id = request.POST.get('id')

    try:
        supplier = Supplier.objects.get(id=supplier_id)

        data = {
            'id': supplier.id,
            'name': supplier.name,
            'phone': supplier.phone,
            'email': supplier.email,
            'gstin': supplier.gstin,
            'address': supplier.address,
        }

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supplier with the provided ID does not exist.'}, status=404)

    return JsonResponse(data)


@login_required
@require_POST
def search_supplier(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    suppliers_list = Supplier.objects.filter(name__icontains=search_text)
    suppliers = render(request, 'transactions/supplier-search.html', {'suppliers': suppliers_list}).content.decode('utf-8')

    return JsonResponse({'suppliers': suppliers})


@login_required
def purchases(request):

    purchases_list = list(PurchaseItem.objects.filter().order_by('-updated_at'))

    paginator = Paginator(purchases_list, 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Transactions', 'url': ''},
        {'label': 'Purchases', 'url': '/transactions/purchases/'}
    ]

    context = {
        'pagination': pagination,
        'page_title': 'Purchases',
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'transactions/purchases.html', context)


@login_required
@require_POST
def new_purchase(request):

    supplier_data = {
        'id': request.POST.get('supplier[id]'),
        'phone': request.POST.get('supplier[phone]'),
        'address': request.POST.get('supplier[address]'),
        'email': request.POST.get('supplier[email]'),
        'gstin': request.POST.get('supplier[gstin]')
    }

    payment_amount_raw = request.POST.get('paymentDetails[paymentAmount]')
    discount_value_raw = request.POST.get('discountDetails[discountValue]')
    labour_making_charge__value_raw = request.POST.get('chargeDetails[labourMakingChargeValue]')
    gst_raw = request.POST.get('taxDetails[gst]')

    payment_data = {
        'payment_method': request.POST.get('paymentDetails[paymentMethod]'),
        'payment_amount': Decimal(payment_amount_raw) if payment_amount_raw else Decimal('0.00')
    }

    discount_data = {
        'discount_type': request.POST.get('discountDetails[discountType]'),
        'discount_value': Decimal(discount_value_raw) if discount_value_raw else Decimal('0.00'),
        'discount_note': request.POST.get('discountDetails[discountNote]')
    }

    charges_data = {
        'labour_making_charge_type': request.POST.get('chargeDetails[labourMakingChargeType]'),
        'labour_making_charge_value': Decimal(labour_making_charge__value_raw) if labour_making_charge__value_raw else Decimal('0.00'),
        'labour_making_charge_note': request.POST.get('chargeDetails[labourMakingChargeNote]')
    }

    tax_data = {
        'gst': Decimal(gst_raw) if gst_raw else Decimal('0.00'),
    }

    products_data = []

    for key in request.POST.keys():
        if key.startswith('products'):

            index = int(key.split('[')[1].split(']')[0])
            attribute = key.split('[')[2].split(']')[0]
            value = request.POST[key]

            if index >= len(products_data):
                products_data.append({})

            products_data[index][attribute] = value

    if products_data:

        try:
            supplier_id = supplier_data.get('id')
            supplier = Supplier.objects.get(id=supplier_id)

            purchase_bill = PurchaseBill.objects.create(
                supplier=supplier,
                **payment_data,
                **discount_data,
                **charges_data
            )

            for product in products_data:

                stock_id = product.get('id')
                weight = float(product.get('weight', 0))
                quantity = int(product.get('quantity', 0))
                stock_note = product.get('stockNote', '')
                total_price = float(product.get('totalPrice', 0))
                price_per_item = float(product.get('pricePerItem', 0))

                stock = Stock.objects.get(id=stock_id)

                # stock.quantity += quantity
                # stock.weight = float(stock.weight or 0) + weight
                # stock.purchase_price = float(stock.purchase_price or 0) + total_price

                # stock.save()

                PurchaseItem.objects.create(
                    billno=purchase_bill,
                    stock=stock,
                    stock_note=stock_note,
                    quantity=quantity,
                    weight=weight,
                    perprice=price_per_item,
                    totalprice=total_price
                )

            PurchaseBillDetails.objects.create(
                billno=purchase_bill,
                **tax_data
            )

            return JsonResponse({'status': 'success', 'message': 'Purchase added successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'No purchase data provided'}, status=400)


@login_required
@require_POST
def get_purchase(request):

    purchase_id = request.POST.get('id')

    purchase = PurchaseItem.objects.filter(billno=purchase_id).values(
        'billno__billno',
        'billno__time',
        'billno__supplier__id',
        'billno__supplier__name',
        'billno__supplier__phone',
        'billno__supplier__email',
        'billno__supplier__gstin',
        'billno__supplier__address',
        'stock__id',
        'stock__name',
        'quantity',
        'weight',
        'perprice',
        'stock_note',
        'totalprice',
        'billno__payment_method',
        'billno__payment_amount',
        'billno__remaining_amount',
        'billno__discount_type',
        'billno__discount_value',
        'billno__discount_note',
        'billno__labour_making_charge_type',
        'billno__labour_making_charge_value',
        'billno__labour_making_charge_note',
    )

    try:
        tax_details = PurchaseBillDetails.objects.get(billno_id=purchase_id)

        tax_details_dict = {
            'gst': tax_details.gst,
            'gst_amount': tax_details.gst_amount,
            'total': tax_details.total,
            'total_after_discount': tax_details.total_after_discount,
            'total_discount': tax_details.total_discount,
            'total_labour_making_charge': tax_details.total_labour_making_charge,
            'total_weight': tax_details.total_weight
        }

    except PurchaseBillDetails.DoesNotExist:
        tax_details_dict = {}

    return JsonResponse({'purchase': list(purchase), 'tax_details': tax_details_dict})


@login_required
@require_POST
def update_purchase(request):

    purchase_id = request.POST.get('id')
    total_after_discount = request.POST.get('total_after_discount')
    total_discount = request.POST.get('total_discount')
    payment_amount = request.POST.get('payment_amount')
    remaining_amount = request.POST.get('remaining_amount')

    try:
        purchase_details = PurchaseBillDetails.objects.get(billno=purchase_id)
        purchase_bill = purchase_details.billno

        if total_after_discount:
            purchase_details.total_after_discount = Decimal(total_after_discount)

        if total_discount:
            purchase_details.total_discount = Decimal(total_discount)

        purchase_details.save()

        if payment_amount:
            purchase_bill.payment_amount = Decimal(payment_amount)

        if remaining_amount:
            purchase_bill.remaining_amount = Decimal(remaining_amount)

        purchase_bill.save(update_fields=['payment_amount', 'remaining_amount'])

        return JsonResponse({'success': True})

    except PurchaseBillDetails.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Purchase details not found'})


@login_required
@require_POST
def delete_purchase(request):

    purchase_id = request.POST.get('id')

    try:
        purchase = PurchaseBill.objects.get(pk=purchase_id)
        purchase.delete()

        return JsonResponse({'status': 'success', 'message': 'Purchase deleted successfully'})

    except PurchaseBill.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Purchase not found'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def search_purchase(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    purchases_list = list(PurchaseItem.objects.filter(billno__supplier__name__icontains=search_text))
    purchases = render(request, 'transactions/purchase-search.html', {'purchases': list(purchases_list)}).content.decode('utf-8')

    return JsonResponse({'purchases': purchases})


@login_required
def sales(request):

    sales_list = list(SaleItem.objects.filter().order_by('-updated_at'))

    paginator = Paginator(sales_list, 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Transactions', 'url': ''},
        {'label': 'Sales', 'url': '/transactions/sales/'}
    ]

    context = {
        'pagination': pagination,
        'page_title': 'Sales',
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'transactions/sales.html', context)


@login_required
@require_POST
def new_sale(request):

    customer_data = {
        'name': request.POST.get('customer[name]'),
        'phone': request.POST.get('customer[phone]'),
        'email': request.POST.get('customer[email]'),
        'gstin': request.POST.get('customer[gstin]'),
        'address': request.POST.get('customer[address]')
    }

    payment_amount_raw = request.POST.get('paymentDetails[paymentAmount]')
    discount_value_raw = request.POST.get('discountDetails[discountValue]')
    labour_making_charge__value_raw = request.POST.get('chargeDetails[labourMakingChargeValue]')
    gst_raw = request.POST.get('taxDetails[gst]')

    payment_data = {
        'payment_method': request.POST.get('paymentDetails[paymentMethod]'),
        'payment_amount': Decimal(payment_amount_raw) if payment_amount_raw else Decimal('0.00')
    }

    discount_data = {
        'discount_type': request.POST.get('discountDetails[discountType]'),
        'discount_value': Decimal(discount_value_raw) if discount_value_raw else Decimal('0.00'),
        'discount_note': request.POST.get('discountDetails[discountNote]')
    }

    charges_data = {
        'labour_making_charge_type': request.POST.get('chargeDetails[labourMakingChargeType]'),
        'labour_making_charge_value': Decimal(labour_making_charge__value_raw) if labour_making_charge__value_raw else Decimal('0.00'),
        'labour_making_charge_note': request.POST.get('chargeDetails[labourMakingChargeNote]')
    }

    tax_data = {
        'gst': Decimal(gst_raw) if gst_raw else Decimal('0.00'),
    }

    products_data = []

    for key in request.POST.keys():
        if key.startswith('products'):

            index = int(key.split('[')[1].split(']')[0])
            attribute = key.split('[')[2].split(']')[0]
            value = request.POST[key]

            if index >= len(products_data):
                products_data.append({})

            products_data[index][attribute] = value

    if products_data:

        try:
            customer = None

            if customer_data['phone']:
                customer = Customer.objects.filter(phone=customer_data['phone']).first()

            if not customer:
                customer = Customer.objects.create(
                    name=customer_data['name'],
                    phone=customer_data['phone'],
                    email=customer_data['email'],
                    gstin=customer_data['gstin'],
                    address=customer_data['address'],
                )

            sale_bill = SaleBill.objects.create(
                customer=customer,
                **payment_data,
                **discount_data,
                **charges_data
            )

            for product in products_data:

                stock_id = product.get('id')
                weight = float(product.get('weight', 0))
                quantity = int(product.get('quantity', 0))
                stock_note = product.get('stockNote', '')
                total_price = float(product.get('totalPrice', 0))
                price_per_item = float(product.get('pricePerItem', 0))

                stock = Stock.objects.get(id=stock_id)

                stock.quantity -= quantity
                stock.weight = float(stock.weight) - weight if stock.weight else 0

                stock.save()

                SaleItem.objects.create(
                    billno=sale_bill,
                    stock=stock,
                    stock_note=stock_note,
                    quantity=quantity,
                    weight=weight,
                    perprice=price_per_item,
                    totalprice=total_price
                )

            SaleBillDetails.objects.create(
                billno=sale_bill,
                **tax_data
            )

            return JsonResponse({'status': 'success', 'message': 'Sale added successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'No sale data provided'}, status=400)


@login_required
@require_POST
def get_sale(request):

    sale_id = request.POST.get('id')

    sale = SaleItem.objects.filter(billno=sale_id).values(
        'billno__billno',
        'billno__time',
        'billno__customer__id',
        'billno__customer__name',
        'billno__customer__phone',
        'billno__customer__address',
        'billno__customer__email',
        'billno__customer__gstin',
        'stock__id',
        'stock__name',
        'quantity',
        'weight',
        'stock_note',
        'perprice',
        'totalprice',
        'billno__payment_method',
        'billno__payment_amount',
        'billno__remaining_amount',
        'billno__discount_type',
        'billno__discount_value',
        'billno__discount_note',
        'billno__labour_making_charge_type',
        'billno__labour_making_charge_value',
        'billno__labour_making_charge_note',
    )

    try:
        tax_details = SaleBillDetails.objects.get(billno_id=sale_id)

        tax_details_dict = {
            'gst': tax_details.gst,
            'gst_amount': tax_details.gst_amount,
            'total': tax_details.total,
            'total_after_discount': tax_details.total_after_discount,
            'total_discount': tax_details.total_discount,
            'total_labour_making_charge': tax_details.total_labour_making_charge,
            'total_weight': tax_details.total_weight
        }

    except SaleBillDetails.DoesNotExist:
        tax_details_dict = {}

    return JsonResponse({'sale': list(sale), 'tax_details': tax_details_dict})


@login_required
@require_POST
def update_sale(request):

    sale_id = request.POST.get('id')
    total_after_discount = request.POST.get('total_after_discount')
    total_discount = request.POST.get('total_discount')
    payment_amount = request.POST.get('payment_amount')
    remaining_amount = request.POST.get('remaining_amount')

    try:
        sale_details = SaleBillDetails.objects.get(billno=sale_id)
        sale_bill = sale_details.billno

        if total_after_discount:
            sale_details.total_after_discount = Decimal(total_after_discount)

        if total_discount:
            sale_details.total_discount = Decimal(total_discount)

        sale_details.save()

        if payment_amount:
            sale_bill.payment_amount = Decimal(payment_amount)

        if remaining_amount:
            sale_bill.remaining_amount = Decimal(remaining_amount)

        sale_bill.save(update_fields=['payment_amount', 'remaining_amount'])

        return JsonResponse({'success': True})

    except SaleBillDetails.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sale details not found'})


@login_required
@require_POST
def delete_sale(request):
    sale_id = request.POST.get('id')

    try:
        sale = SaleBill.objects.get(pk=sale_id)

        with transaction.atomic():
            sale_items = SaleItem.objects.filter(billno=sale)

            for item in sale_items:
                stock = item.stock

                stock.quantity += item.quantity
                stock.weight += item.weight or 0

                stock.save()

            sale.delete()

        return JsonResponse({'status': 'success', 'message': 'Sale deleted successfully'})

    except SaleBill.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sale not found'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def search_sale(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    sales_list = list(SaleItem.objects.filter(billno__customer__name__icontains=search_text))
    sales = render(request, 'transactions/sale-search.html', {'sales': list(sales_list)}).content.decode('utf-8')

    return JsonResponse({'sales': sales})


@login_required
def customers(request):

    customer_list = list(Customer.objects.filter().order_by('-updated_at'))

    paginator = Paginator(customer_list, 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Transactions', 'url': ''},
        {'label': 'Customers', 'url': '/transactions/customers/'}
    ]

    context = {
        'pagination': pagination,
        'page_title': 'Customers',
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'transactions/customers.html', context)


@login_required
@require_POST
def new_customer(request):

    attr_dict = request.POST.dict()

    try:
        Customer.objects.create(**attr_dict)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error adding customer: {str(e)}'}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Customer added successfully'})


@login_required
@require_POST
def get_customers(request):
    customers_list = Customer.objects.filter().values('id', 'name', 'phone', 'address', 'email', 'gstin')
    return JsonResponse({'customers': list(customers_list)})


@login_required
@require_POST
def edit_customer(request):

    customer_id = request.POST.get('id')
    customer_name = request.POST.get('name')
    customer_phone = request.POST.get('phone')
    customer_email = request.POST.get('email')
    customer_gstin = request.POST.get('gstin')
    customer_address = request.POST.get('address')

    try:
        customer = Customer.objects.get(pk=customer_id)

        if customer_name:
            customer.name = customer_name

        if customer_phone:
            customer.phone = customer_phone

        if customer_email:
            customer.email = customer_email

        if customer_gstin:
            customer.gstin = customer_gstin

        if customer_address:
            customer.address = customer_address

        customer.save()

    except ObjectDoesNotExist as e1:
        return JsonResponse({'status': 'error', 'message': 'Customer with the provided ID does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Customer updated successfully.'})


@login_required
@require_POST
def delete_customer(request):

    customer_id = request.POST.get('id')

    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Customer with the provided ID does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Customer deleted successfully.'})


@login_required
@require_POST
def customer_details(request):

    customer_id = request.POST.get('id')

    try:
        customer = Customer.objects.get(id=customer_id)

        data = {
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'email': customer.email,
            'gstin': customer.gstin,
            'address': customer.address,
            'created_at': customer.created_at
        }

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Customer with the provided ID does not exist.'}, status=404)

    return JsonResponse(data)


@login_required
@require_POST
def search_customer(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    customers_list = Customer.objects.filter(name__icontains=search_text)
    customers = render(request, 'transactions/customer-search.html', {'customers': customers_list}).content.decode('utf-8')

    return JsonResponse({'customers': customers})

@login_required
@require_POST
def customer_suggestions(request):

    query = request.POST.get('query', '')

    if not query:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    customers_list = Customer.objects.filter(name__icontains=query).values('id', 'name')
    return JsonResponse(list(customers_list), safe=False)
