from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from stock.constants import LockerNumberChoices
from .models import Giravee, GiraveeTransaction
from .utils import parse_fields_from_request
from django.http import JsonResponse
from django.shortcuts import render


@login_required
def giravee(request):

    giravee_list = Giravee.objects.filter().order_by('-start_date')

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
        transactions = giravee.transactions.order_by('-date')

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

        add_amount = float(data.get('add_amount', 0))
        deposit_date = data.get('deposit_date')
        note = data.get('add_note', '')

        if add_amount and add_amount > 0:

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

    if not giravee_id:
        return JsonResponse({'status': 'error', 'message': 'Giravee ID is required.'}, status=400)

    try:
        giravee = Giravee.objects.get(id=giravee_id)
        giravee.delete()

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Giravee not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'success', 'message': 'Giravee deleted successfully.'})


@login_required
@require_POST
def search_giravee(request):

    search_text = request.POST.get('search_text', '')

    if not search_text:
        return JsonResponse({'status': 'error', 'message': 'Search term missing'}, status=400)

    giravee_list = Giravee.objects.filter(name__icontains=search_text).order_by('-start_date')
    giravees_html = render(request, 'giravee/giravee-search.html', {'giravees': giravee_list}).content.decode('utf-8')

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
