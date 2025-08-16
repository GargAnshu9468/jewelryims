from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from stock.constants import LockerNumberChoices, InterestChoices
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from .models import Giravee, GiraveeTransaction
from django.utils.dateparse import parse_date
from .utils import parse_fields_from_request
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q


@login_required
def giravee(request):

    giravee_list = Giravee.objects.filter(is_cleared=False).order_by('-id')

    paginator = Paginator(list(giravee_list), 6)
    page_number = request.GET.get('page')

    try:
        pagination = paginator.page(page_number)

    except PageNotAnInteger:
        pagination = paginator.page(1)

    except EmptyPage:
        pagination = paginator.page(paginator.num_pages)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Giravee', 'url': '/giravee/'}
    ]

    context = {
        'page_title': 'Giravee',
        'pagination': pagination,
        'breadcrumbs': breadcrumbs,
        'locker_choices': LockerNumberChoices.choices(),
        'interest_choices': InterestChoices.choices(),
    }

    return render(request, 'giravee/giravee.html', context)


@login_required
@require_POST
def get_giravees(request):

    giravee_id = request.POST.get('id')

    if not giravee_id:
        return JsonResponse({'status': 'error', 'message': 'Giravee ID is required.'}, status=400)

    giravees = Giravee.objects.filter(id=giravee_id)
    giravee_list = list(giravees.values())

    transactions_data = []

    if giravees.exists():
        giravee = giravees.first()
        transactions = giravee.transactions.order_by('-id')

        transactions_data = [{
            'id': txn.id,
            'amount': float(txn.amount),
            'date': txn.date.strftime('%Y-%m-%d'),
            'note': txn.note or ''
        } for txn in transactions]

    return JsonResponse({
        'giravees': giravee_list,
        'transactions': transactions_data
    })


@login_required
@require_POST
def add_giravee(request):

    try:
        data = request.POST.dict()

        parsed_data = parse_fields_from_request(data, Giravee)
        Giravee.objects.create(**parsed_data)

        return JsonResponse({'status': 'success', 'message': 'Giravee added successfully'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def edit_giravee(request):

    giravee_id = request.POST.get('id')

    if not giravee_id:
        return JsonResponse({'status': 'error', 'message': 'Giravee ID is required.'}, status=400)

    try:
        data = request.POST.dict()
        parsed_data = parse_fields_from_request(data, Giravee)

        giravee = Giravee.objects.get(id=giravee_id)

        for key, value in parsed_data.items():
            if key != 'id':
                setattr(giravee, key, value)

        giravee.save()

        add_amount = data.get('add_amount', 0)
        deposit_date = data.get('deposit_date')
        note = data.get('add_note', '')

        if add_amount:
            add_amount = float(add_amount)

            txn_attrs = {
                'giravee': giravee,
                'amount': add_amount,
                'note': note
            }

            if deposit_date:
                txn_attrs['date'] = deposit_date

            GiraveeTransaction.objects.create(**txn_attrs)

        return JsonResponse({'status': 'success', 'message': 'Giravee updated successfully.'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Giravee not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def delete_giravee(request):

    giravee_id = request.POST.get('id')
    search_text = request.POST.get('search_text', '').strip()
    start_date_str = request.POST.get('start_date', '').strip()
    end_date_str = request.POST.get('end_date', '').strip()

    if giravee_id:

        try:
            giravee = Giravee.objects.get(id=giravee_id)
            giravee.delete()

            return JsonResponse({'status': 'success', 'message': 'Giravee deleted successfully.'})

        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Giravee not found.'}, status=404)

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
        query &= Q(start_date__range=(start_date, end_date))

    elif start_date:
        query &= Q(start_date__gte=start_date)

    elif end_date:
        query &= Q(start_date__lte=end_date)

    try:
        deleted_count, _ = Giravee.objects.filter(query).delete()

        if deleted_count == 0:
            return JsonResponse({'status': 'info', 'message': 'No matching giravees found to delete.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': f'{deleted_count} giravees deleted successfully.'})


@login_required
@require_POST
def search_giravee(request):

    search_text = request.POST.get('search_text', '').strip()
    start_date_str = request.POST.get('start_date', '').strip()
    end_date_str = request.POST.get('end_date', '').strip()

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
        query &= Q(start_date__range=(start_date, end_date))

    elif start_date:
        query &= Q(start_date__gte=start_date)

    elif end_date:
        query &= Q(start_date__lte=end_date)

    giravee_list = Giravee.objects.filter(query).order_by('-id')

    giravees_html = render(
        request,
        'giravee/giravee-search.html',
        {'giravees': giravee_list}
    ).content.decode('utf-8')

    return JsonResponse({'giravees': giravees_html})


@login_required
@require_POST
def refresh_giravee(request):

    giravee_id = request.POST.get('id')

    if not giravee_id:
        return JsonResponse({'status': 'error', 'message': 'Giravee ID is required.'}, status=400)

    try:
        giravee = Giravee.objects.get(id=giravee_id)
        giravee.save()

        return JsonResponse({'status': 'Giravee refreshed successfully'})

    except Giravee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Giravee not found'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
