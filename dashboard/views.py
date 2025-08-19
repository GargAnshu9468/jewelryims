from transactions.models import Stock, Supplier, PurchaseItem, SaleItem, SaleBill, Customer
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.shortcuts import render
from django.db.models import Sum, F
from giravee.models import Giravee


@login_required
def dashboard(request):

    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)

    breadcrumbs = [
        {'label': 'IMS', 'url': ''},
        {'label': 'Dashboard', 'url': '/'}
    ]

    # Total Inventory Value: Use weighted value (purchase_price * quantity)
    total_inventory_value = Stock.objects.aggregate(
        total_value=Sum(F('purchase_price'))
    )['total_value'] or 0

    total_number_of_items = Stock.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    low_stock_items = Stock.objects.filter(quantity__lt=5, quantity__gt=0).count()
    out_of_stock_items = Stock.objects.filter(quantity=0).count()

    # Stock Turnover Ratio
    stock_turnover_ratio = round(
        (total_number_of_items / (total_inventory_value / 365)), 2
    ) if total_inventory_value > 0 else 0

    # Sales and Purchase Totals
    total_sales_value = SaleItem.objects.aggregate(
        total=Sum('totalprice')
    )['total'] or 0

    total_purchases_value = PurchaseItem.objects.aggregate(
        total=Sum('totalprice')
    )['total'] or 0

    gross_profit_margin = (
        (total_sales_value - total_purchases_value) / total_sales_value * 100
    ) if total_sales_value > 0 else 0

    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()

    # Top selling/purchased items by quantity
    top_selling_items = SaleItem.objects.values(
        item_name=F('stock__name')
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    top_purchasing_items = PurchaseItem.objects.values(
        item_name=F('stock__name')
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]

    net_profit = total_sales_value - total_purchases_value

    profit_margin = (
        (net_profit / total_sales_value) * 100
    ) if total_sales_value > 0 else 0

    total_orders = SaleBill.objects.count()

    average_order_value = (
        total_sales_value / total_orders
    ) if total_orders > 0 else 0

    total_customers_last_month = SaleBill.objects.filter(
        time__month=last_month.month,
        time__year=last_month.year
    ).values('customer').distinct().count()

    customer_acquisition = total_customers - total_customers_last_month

    sales_growth = (
        (total_sales_value - total_purchases_value) / total_purchases_value * 100
    ) if total_purchases_value > 0 else 0

    return_on_investment = (
        (net_profit / total_purchases_value) * 100
    ) if total_purchases_value > 0 else 0

    churn_rate = (
        (total_customers_last_month - total_customers) / total_customers_last_month * 100
    ) if total_customers_last_month > 0 else 0

    total_giravee_amount = Giravee.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_collected_interest = Giravee.objects.filter(is_cleared=True).aggregate(
        total=Sum('interest_amount')
    )['total'] or 0

    context = {
        "page_title": "Dashboard",
        "breadcrumbs": breadcrumbs,
        "total_inventory_value": round(total_inventory_value, 2),
        "total_number_of_items": total_number_of_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "stock_turnover_ratio": stock_turnover_ratio,
        "gross_profit_margin": round(gross_profit_margin, 2),
        "total_sales_value": round(total_sales_value, 2),
        "total_purchases_value": round(total_purchases_value, 2),
        "total_suppliers": total_suppliers,
        "total_customers": total_customers,
        "top_selling_items": top_selling_items,
        "top_purchasing_items": top_purchasing_items,
        "net_profit": round(net_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "total_orders": total_orders,
        "average_order_value": round(average_order_value, 2),
        "customer_acquisition": customer_acquisition,
        "sales_growth": round(sales_growth, 2),
        "return_on_investment": round(return_on_investment, 2),
        "churn_rate": round(churn_rate, 2),
        "total_giravee_amount": round(total_giravee_amount, 2),
        "total_collected_interest": round(total_collected_interest, 2),
    }

    return render(request, "dashboard/dashboard.html", context)
