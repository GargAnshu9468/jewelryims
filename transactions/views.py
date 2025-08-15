from .models import Stock, Supplier, PurchaseItem, PurchaseBill, SaleItem, SaleBill, PurchaseBillDetails, SaleBillDetails, Customer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
from giravee.utils import parse_fields_from_request
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.db.models import Sum
from giravee.utils import Trim
from decimal import Decimal


@login_required
def suppliers(request):

    suppliers_list = Supplier.objects.filter().order_by('-date')

    paginator = Paginator(list(suppliers_list), 6)
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

    suppliers_list = Supplier.objects.filter().values()
    return JsonResponse({'suppliers': list(suppliers_list)})


@login_required
@require_POST
def new_supplier(request):

    try:
        data = request.POST.dict()
        parsed_data = parse_fields_from_request(data, Supplier)

        Supplier.objects.create(**parsed_data)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error adding supplier: {str(e)}'}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Supplier added successfully'})


@login_required
@require_POST
def edit_supplier(request):

    try:
        data = request.POST.dict()
        supplier_id = data.get('id')

        if not supplier_id:
            return JsonResponse({'status': 'error', 'message': 'Supplier ID is required.'}, status=400)
    
        supplier = Supplier.objects.get(id=supplier_id)
        parsed_data = parse_fields_from_request(data, Supplier)

        for key, value in parsed_data.items():
            if key != 'id':
                setattr(supplier, key, value)

        supplier.save()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supplier not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Supplier updated successfully.'})


@login_required
@require_POST
def delete_supplier(request):

    supplier_id = request.POST.get('id')

    if not supplier_id:
        return JsonResponse({'status': 'error', 'message': 'Supplier ID is required.'}, status=400)

    try:
        supplier = Supplier.objects.get(id=supplier_id)
        supplier.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Supplier not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Supplier deleted successfully.'})


@login_required
@require_POST
def supplier_details(request):

    supplier_id = request.POST.get('id')

    if not supplier_id:
        return JsonResponse({'status': 'error', 'message': 'Supplier ID is required.'}, status=400)

    supplier = Supplier.objects.filter(id=supplier_id).values().first()

    if not supplier:
        return JsonResponse({'status': 'error', 'message': 'Supplier not found.'}, status=404)

    return JsonResponse(supplier)


@login_required
@require_POST
def search_supplier(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    suppliers_list = Supplier.objects.filter(name__icontains=search_text).order_by('-date')
    suppliers = render(request, 'transactions/supplier-search.html', {'suppliers': list(suppliers_list)}).content.decode('utf-8')

    return JsonResponse({'suppliers': suppliers})


@login_required
def purchases(request):

    purchases_list = PurchaseItem.objects.filter().order_by('-id')

    paginator = Paginator(list(purchases_list), 6)
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
        'payment_amount': float(payment_amount_raw) if payment_amount_raw else 0
    }

    discount_data = {
        'discount_type': request.POST.get('discountDetails[discountType]'),
        'discount_value': float(discount_value_raw) if discount_value_raw else 0,
        'discount_note': request.POST.get('discountDetails[discountNote]')
    }

    charges_data = {
        'labour_making_charge_type': request.POST.get('chargeDetails[labourMakingChargeType]'),
        'labour_making_charge_value': float(labour_making_charge__value_raw) if labour_making_charge__value_raw else 0,
        'labour_making_charge_note': request.POST.get('chargeDetails[labourMakingChargeNote]')
    }

    tax_data = {
        'gst': float(gst_raw) if gst_raw else 0,
    }

    purchase_time = request.POST.get('time')
    other_data = {'time': purchase_time} if purchase_time else {}

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
                **charges_data,
                **other_data
            )

            for product in products_data:

                stock_id = product.get('id')
                weight = float(product.get('weight', 0))
                quantity = int(product.get('quantity', 0))
                stock_note = product.get('stockNote', '')
                total_price = float(product.get('totalPrice', 0))
                price_per_item = float(product.get('pricePerItem', 0))

                stock = Stock.objects.get(id=stock_id)

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

    if not purchase_id:
        return JsonResponse({'status': 'error', 'message': 'Purchase ID is required.'}, status=400)

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

    tax_details = PurchaseBillDetails.objects.filter(billno_id=purchase_id).values().first() or {}
    bill = PurchaseBill.objects.select_related('supplier').get(pk=purchase_id)

    previous_balance = (
        PurchaseBill.objects
        .filter(supplier=bill.supplier, billno__lt=bill.billno)
        .aggregate(total=Sum('remaining_amount'))
        .get('total') or Decimal('0.00')
    )

    return JsonResponse({
        'purchase': list(purchase),
        'tax_details': tax_details,
        'previous_balance': str(previous_balance)
    })


@login_required
@require_POST
def update_purchase(request):

    purchase_id = request.POST.get('id')

    if not purchase_id:
        return JsonResponse({'success': False, 'message': 'Purchase ID is required.'})

    remaining_amount = request.POST.get('remaining_amount')
    payment_amount = request.POST.get('payment_amount')

    try:
        purchase_bill = PurchaseBill.objects.get(billno=purchase_id)

        if payment_amount:
            purchase_bill.payment_amount = float(payment_amount)

        if remaining_amount:
            purchase_bill.remaining_amount = float(remaining_amount)

        purchase_bill.save(update_fields=['payment_amount', 'remaining_amount'])
        return JsonResponse({'success': True})

    except PurchaseBill.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Purchase details not found'})

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})


@login_required
@require_POST
def delete_purchase(request):

    purchase_id = request.POST.get('id')

    if not purchase_id:
        return JsonResponse({'status': 'error', 'message': 'Purchase ID is required.'}, status=400)

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
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    purchases_list = PurchaseItem.objects.filter(billno__supplier__name__icontains=search_text).order_by('-date')
    purchases = render(request, 'transactions/purchase-search.html', {'purchases': list(purchases_list)}).content.decode('utf-8')

    return JsonResponse({'purchases': purchases})


@login_required
def sales(request):

    sales_list = SaleItem.objects.filter().order_by('-id')

    paginator = Paginator(list(sales_list), 6)
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
        'payment_amount': float(payment_amount_raw) if payment_amount_raw else 0
    }

    discount_data = {
        'discount_type': request.POST.get('discountDetails[discountType]'),
        'discount_value': float(discount_value_raw) if discount_value_raw else 0,
        'discount_note': request.POST.get('discountDetails[discountNote]')
    }

    charges_data = {
        'labour_making_charge_type': request.POST.get('chargeDetails[labourMakingChargeType]'),
        'labour_making_charge_value': float(labour_making_charge__value_raw) if labour_making_charge__value_raw else 0,
        'labour_making_charge_note': request.POST.get('chargeDetails[labourMakingChargeNote]')
    }

    tax_data = {
        'gst': float(gst_raw) if gst_raw else 0,
    }

    sale_time = request.POST.get('time')
    other_data = {'time': sale_time} if sale_time else {}

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

            elif customer_data['name']:
                customer = Customer.objects.annotate(
                    trimmed_name=Trim('name')
                ).filter(trimmed_name__iexact=customer_data['name'].strip()).first()

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
                **charges_data,
                **other_data
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

    if not sale_id:
        return JsonResponse({'status': 'error', 'message': 'Sale ID is required.'}, status=400)

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

    tax_details = SaleBillDetails.objects.filter(billno_id=sale_id).values().first() or {}
    bill = SaleBill.objects.select_related('customer').get(pk=sale_id)

    previous_balance = (
        SaleBill.objects
        .filter(customer=bill.customer, billno__lt=bill.billno)
        .aggregate(total=Sum('remaining_amount'))
        .get('total') or Decimal('0.00')
    )

    return JsonResponse({
        'sale': list(sale),
        'tax_details': tax_details,
        'previous_balance': str(previous_balance)
    })


@login_required
@require_POST
def update_sale(request):

    sale_id = request.POST.get('id')

    if not sale_id:
        return JsonResponse({'success': False, 'message': 'Sale ID is required.'})

    remaining_amount = request.POST.get('remaining_amount')
    payment_amount = request.POST.get('payment_amount')

    try:
        sale_bill = SaleBill.objects.get(billno=sale_id)

        if payment_amount:
            sale_bill.payment_amount = float(payment_amount)

        if remaining_amount:
            sale_bill.remaining_amount = float(remaining_amount)

        sale_bill.save(update_fields=['payment_amount', 'remaining_amount'])
        return JsonResponse({'success': True})

    except SaleBill.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sale details not found'})

    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)})


@login_required
@require_POST
def delete_sale(request):

    sale_id = request.POST.get('id')

    if not sale_id:
        return JsonResponse({'status': 'error', 'message': 'Sale ID is required.'}, status=400)

    try:
        sale = SaleBill.objects.get(pk=sale_id)

        # with transaction.atomic():
        #     sale_items = SaleItem.objects.filter(billno=sale)

        #     for item in sale_items:
        #         stock = item.stock

        #         stock.quantity += item.quantity
        #         stock.weight += item.weight or 0

        #         stock.save()

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
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    sales_list = SaleItem.objects.filter(billno__customer__name__icontains=search_text).order_by('-date')
    sales = render(request, 'transactions/sale-search.html', {'sales': list(sales_list)}).content.decode('utf-8')

    return JsonResponse({'sales': sales})


@login_required
def customers(request):

    customer_list = Customer.objects.filter().order_by('-date')

    paginator = Paginator(list(customer_list), 6)
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

    try:
        data = request.POST.dict()
        parsed_data = parse_fields_from_request(data, Customer)

        Customer.objects.create(**parsed_data)

    except Exception as e:
        print(str(e))
        return JsonResponse({'status': 'error', 'message': f'Error adding customer: {str(e)}'}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Customer added successfully'})


@login_required
@require_POST
def get_customers(request):

    customers_list = Customer.objects.filter().values()
    return JsonResponse({'customers': list(customers_list)})


@login_required
@require_POST
def edit_customer(request):

    try:
        data = request.POST.dict()
        customer_id = data.get('id')

        if not customer_id:
            return JsonResponse({'status': 'error', 'message': 'Customer ID is required.'}, status=400)

        customer = Customer.objects.get(pk=customer_id)
        parsed_data = parse_fields_from_request(data, Customer)

        for key, value in parsed_data.items():
            if key != 'id':
                setattr(customer, key, value)

        customer.save()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Customer not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Customer updated successfully.'})


@login_required
@require_POST
def delete_customer(request):

    customer_id = request.POST.get('id')

    if not customer_id:
        return JsonResponse({'status': 'error', 'message': 'Customer ID is required.'}, status=400)

    try:
        customer = Customer.objects.get(id=customer_id)
        customer.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Customer not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Customer deleted successfully.'})


@login_required
@require_POST
def customer_details(request):

    customer_id = request.POST.get('id')

    if not customer_id:
        return JsonResponse({'status': 'error', 'message': 'Customer ID is required.'}, status=400)

    customer = Customer.objects.filter(id=customer_id).values().first()

    if not customer:
        return JsonResponse({'status': 'error', 'message': 'Customer not found.'}, status=404)

    return JsonResponse(customer)


@login_required
@require_POST
def search_customer(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    customers_list = Customer.objects.filter(name__icontains=search_text).order_by('-date')
    customers = render(request, 'transactions/customer-search.html', {'customers': list(customers_list)}).content.decode('utf-8')

    return JsonResponse({'customers': customers})


@login_required
@require_POST
def customer_suggestions(request):

    query = request.POST.get('query', '')

    if not query:
        return JsonResponse({'status': 'error', 'message': 'Suggestion query missing'}, status=400)

    customers_list = Customer.objects.filter(name__icontains=query).values('id', 'name')
    return JsonResponse(list(customers_list), safe=False)
