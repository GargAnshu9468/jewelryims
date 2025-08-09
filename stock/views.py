from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .constants import MaterialChoices, CategoryChoices, KaratChoices
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render
from django.db import models
from .models import Stock


@login_required
def stock(request):

    stocks_list = list(Stock.objects.filter(is_deleted=False).order_by('-updated_at'))

    paginator = Paginator(stocks_list, 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Stock', 'url': '/stock/'}
    ]

    context = {
        'page_title': 'Stock',
        'pagination': pagination,
        'breadcrumbs': breadcrumbs,
        'material_choices': MaterialChoices.choices(),
        'category_choices': CategoryChoices.choices(),
        'karat_choices': KaratChoices.choices(),
    }

    return render(request, 'stock/stock.html', context)


@login_required
@require_POST
def get_stocks(request):
    stock_id = request.POST.get('id')
    filter_attr = {'is_deleted': False}

    if stock_id:
        filter_attr['id'] = stock_id

    stocks_list = Stock.objects.filter(**filter_attr).values()
    return JsonResponse({'stocks': list(stocks_list)})


@login_required
@require_POST
def add_stock(request):
    data = request.POST.dict()

    valid_fields = {field.name for field in Stock._meta.fields}
    stock_data = {}

    for key, value in data.items():
        if key in valid_fields:
            field = Stock._meta.get_field(key)

            if isinstance(field, models.IntegerField):
                stock_data[key] = int(value) if value else 0

            elif isinstance(field, models.DecimalField):
                stock_data[key] = float(value) if value else 0

            elif isinstance(field, models.BooleanField):
                stock_data[key] = value.lower() in ['true', '1']

            else:
                stock_data[key] = value

    try:
        stock = Stock.objects.create(**stock_data)
        return JsonResponse({'status': 'success', 'message': 'Stock added successfully'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error adding stock: {str(e)}'}, status=500)


@login_required
@require_POST
def edit_stock(request):
    stock_id = request.POST.get('id')

    if not stock_id:
        return JsonResponse({'status': 'error', 'message': 'Stock ID is required.'}, status=400)

    try:
        stock = Stock.objects.get(id=stock_id)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Stock with the provided ID does not exist.'}, status=404)

    data = request.POST.dict()

    valid_fields = {field.name for field in Stock._meta.fields}
    updated_fields = {}

    for key, value in data.items():
        if key in valid_fields and key != 'id':
            field = Stock._meta.get_field(key)

            if isinstance(field, models.IntegerField):
                updated_fields[key] = int(value) if value else 0

            elif isinstance(field, models.DecimalField):
                updated_fields[key] = float(value) if value else 0

            elif isinstance(field, models.BooleanField):
                updated_fields[key] = value.lower() in ['true', '1']

            else:
                updated_fields[key] = value

    for key, value in updated_fields.items():
        setattr(stock, key, value)

    try:
        stock.save()
        return JsonResponse({'status': 'success', 'message': 'Stock updated successfully.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error updating stock: {str(e)}'}, status=500)


@login_required
@require_POST
def delete_stock(request):

    stock_id = request.POST.get('id')

    try:
        stock = Stock.objects.get(id=stock_id)
        stock.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Stock with the provided ID does not exist.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'message': 'Stock deleted successfully.'})


@login_required
@require_POST
def search_stock(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided'}, status=400)

    stocks_list = Stock.objects.filter(name__icontains=search_text)
    stocks = render(request, 'stock/stock-search.html', {'stocks': stocks_list}).content.decode('utf-8')

    return JsonResponse({'stocks': stocks})
