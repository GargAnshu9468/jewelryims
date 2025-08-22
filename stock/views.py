from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .constants import MaterialChoices, CategoryChoices, KaratChoices
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from giravee.utils import parse_fields_from_request
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
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
        {'label': 'IMS', 'url': '/'},
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

    data = request.POST.dict()
    stock_id = data.get('id')

    query = {}

    if stock_id:
        query['id'] = stock_id

    stocks_list = Stock.objects.filter(**query).values()
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
    search_text = request.POST.get('search_text', '').strip()
    start_date_str = request.POST.get('start_date', '').strip()
    end_date_str = request.POST.get('end_date', '').strip()

    if stock_id:

        try:
            stock = Stock.objects.get(id=stock_id)
            stock.delete()

            return JsonResponse({'status': 'success', 'message': 'Stock deleted successfully.'})

        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Stock not found.'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    if start_date and end_date and end_date < start_date:
        start_date, end_date = end_date, start_date

    query = Q()

    if search_text:
        query &= Q(name__icontains=search_text)

    if start_date and end_date:
        query &= Q(date__range=(start_date, end_date))

    elif start_date:
        query &= Q(date__gte=start_date)

    elif end_date:
        query &= Q(date__lte=end_date)

    try:
        deleted_count, _ = Stock.objects.filter(query).delete()

        if deleted_count == 0:
            return JsonResponse({'status': 'info', 'message': 'No matching stocks found to delete.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': f'{deleted_count} stocks deleted successfully.'})


@login_required
@require_POST
def search_stock(request):

    search_text = request.POST.get('search_text', '').strip()
    start_date_str = request.POST.get('start_date', '').strip()
    end_date_str = request.POST.get('end_date', '').strip()
    page_number = request.POST.get('page', 1)

    # Parse dates safely

    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Swap if end_date is earlier than start_date

    if start_date and end_date and end_date < start_date:
        start_date, end_date = end_date, start_date

    query = Q()

    if search_text:
        query &= Q(name__icontains=search_text)

    if start_date and end_date:
        query &= Q(date__range=(start_date, end_date))

    elif start_date:
        query &= Q(date__gte=start_date)

    elif end_date:
        query &= Q(date__lte=end_date)

    stocks_list = Stock.objects.filter(query).order_by('-id')
    paginator = Paginator(stocks_list, 6)

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    stocks_html = render(request, 'stock/stock-search.html', {'stocks': pagination}).content.decode('utf-8')
    pagination_html = render(request, 'common/pagination-search.html', {'pagination': pagination}).content.decode('utf-8')

    return JsonResponse({
        'stocks': stocks_html,
        'pagination_html': pagination_html
    })
