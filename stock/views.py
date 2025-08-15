from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .constants import MaterialChoices, CategoryChoices, KaratChoices
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from giravee.utils import parse_fields_from_request
from django.http import JsonResponse
from django.shortcuts import render
from .models import Stock


@login_required
def stock(request):

    stocks_list = Stock.objects.filter().order_by('-id')

    paginator = Paginator(list(stocks_list), 6)
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

    stocks_list = Stock.objects.filter().values()
    return JsonResponse({'stocks': list(stocks_list)})


@login_required
@require_POST
def add_stock(request):

    try:
        data = request.POST.dict()
        parsed_data = parse_fields_from_request(data, Stock)

        Stock.objects.create(**parsed_data)
        return JsonResponse({'status': 'success', 'message': 'Stock added successfully'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Error adding stock: {str(e)}'}, status=500)


@login_required
@require_POST
def edit_stock(request):

    try:
        data = request.POST.dict()
        stock_id = data.get('id')

        if not stock_id:
            return JsonResponse({'status': 'error', 'message': 'Stock ID is required.'}, status=400)

        stock = Stock.objects.get(id=stock_id)
        parsed_data = parse_fields_from_request(data, Stock)

        for key, value in parsed_data.items():
            if key != 'id':
                setattr(stock, key, value)

        stock.save()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Stock not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Stock updated successfully.'})


@login_required
@require_POST
def delete_stock(request):

    stock_id = request.POST.get('id')

    if not stock_id:
        return JsonResponse({'status': 'error', 'message': 'Stock ID is required.'}, status=400)

    try:
        stock = Stock.objects.get(id=stock_id)
        stock.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Stock not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Stock deleted successfully.'})


@login_required
@require_POST
def search_stock(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    stocks_list = Stock.objects.filter(name__icontains=search_text).order_by('-id')
    stocks = render(request, 'stock/stock-search.html', {'stocks': list(stocks_list)}).content.decode('utf-8')

    return JsonResponse({'stocks': stocks})
