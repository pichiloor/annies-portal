from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Sum
from plotly.offline import plot
import plotly.graph_objects as go

from .models import Sale, Purchase, Store


@login_required
def dashboard(request):
    # Filtros
    selected_year = request.GET.get('year', '')
    selected_month = request.GET.get('month', '')
    selected_city = request.GET.get('city', '')
    selected_store = request.GET.get('store', '')

    cache_key = f"dashboard_{selected_year}_{selected_month}_{selected_city}_{selected_store}"
    cached = cache.get(cache_key)
    if cached:
        return render(request, 'dashboard.html', cached)

    # Opciones disponibles
    available_years = sorted(Sale.objects.dates('sales_date', 'year'), reverse=True)
    available_years = [d.year for d in available_years]
    months = [
        (1,'January'),(2,'February'),(3,'March'),(4,'April'),
        (5,'May'),(6,'June'),(7,'July'),(8,'August'),
        (9,'September'),(10,'October'),(11,'November'),(12,'December'),
    ]
    available_cities = Store.objects.values_list('city', flat=True).distinct().order_by('city')
    available_stores = Store.objects.order_by('store_id')
    if selected_city:
        available_stores = available_stores.filter(city=selected_city)

    # Revenue por producto
    sales_qs = Sale.objects.all()
    if selected_year:
        sales_qs = sales_qs.filter(sales_date__year=selected_year)
    if selected_month:
        sales_qs = sales_qs.filter(sales_date__month=selected_month)
    if selected_store:
        sales_qs = sales_qs.filter(store__store_id=selected_store)
    elif selected_city:
        sales_qs = sales_qs.filter(store__city=selected_city)

    sales = sales_qs.values('product_id', 'product__description').annotate(total_revenue=Sum('revenue'), total_qty_sold=Sum('quantity'))

    # Cost por producto
    purchases_qs = Purchase.objects.all()
    if selected_year:
        purchases_qs = purchases_qs.filter(po_date__year=selected_year)
    if selected_month:
        purchases_qs = purchases_qs.filter(po_date__month=selected_month)
    if selected_store:
        purchases_qs = purchases_qs.filter(store__store_id=selected_store)
    elif selected_city:
        purchases_qs = purchases_qs.filter(store__city=selected_city)

    purchases = purchases_qs.values('product_id').annotate(total_cost=Sum('cost'), total_qty_bought=Sum('quantity'))

    # Combinar en un dict por product_id
    cost_map = {p['product_id']: (p['total_cost'], p['total_qty_bought']) for p in purchases}

    results = []
    for s in sales:
        pid = s['product_id']
        name = s['product__description']
        revenue = float(s['total_revenue'])
        qty_sold = int(s['total_qty_sold'])
        cost, qty_bought = (float(cost_map[pid][0]), int(cost_map[pid][1])) if pid in cost_map else (0, 0)
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue > 0 else 0
        results.append({'name': name, 'profit': profit, 'margin': margin, 'has_cost': pid in cost_map, 'revenue': revenue, 'cost': cost, 'qty_sold': qty_sold, 'qty_bought': qty_bought})

    # Top 10 por profit
    top10 = sorted(results, key=lambda x: x['profit'], reverse=True)[:10]

    names = [r['name'] for r in top10]
    profits = [r['profit'] for r in top10]
    margins = [round(r['margin'], 1) for r in top10]

    fig = go.Figure(go.Bar(
        x=profits,
        y=names,
        orientation='h',
        text=[f"${p:,.0f} | {m}%" for p, m in zip(profits, margins)],
        textposition='inside',
    ))
    fig.update_layout(
            title=dict(
        text='<b>Top 10 Products by Profit</b>',
        x=0.5,
        xanchor='center',
    ),
        xaxis_title='Profit ($)',
        yaxis=dict(autorange='reversed'),
        margin=dict(l=200, r=20),
    )

    chart_profit = plot(fig, output_type='div', include_plotlyjs=True)

    # Top 10 por margin — solo productos con costo registrado
    top10_margin = sorted([r for r in results if r['has_cost']], key=lambda x: x['margin'], reverse=True)[:10]
    names_m = [r['name'] for r in top10_margin]
    margins_m = [round(r['margin'], 1) for r in top10_margin]

    fig2 = go.Figure(go.Bar(
        x=margins_m,
        y=names_m,
        orientation='h',
        marker_color='green',
        text=[f"{m}%" for m in margins_m],
        textposition='inside',
    ))
    fig2.update_layout(
        title=dict(
            text='<b>Top 10 Products by Margin</b>',
            x=0.5,
            xanchor='center',
        ),
        xaxis_title='Margin (%)',
        yaxis=dict(autorange='reversed'),
        margin=dict(l=200, r=20),
    )
    chart_margin = plot(fig2, output_type='div', include_plotlyjs=False)

    # --- Vendor charts ---
    sales_vendor = sales_qs.values(
        'product__vendor_id', 'product__vendor__vendor_name'
    ).annotate(total_revenue=Sum('revenue'))

    purchases_vendor = purchases_qs.values(
        'vendor_id', 'vendor__vendor_name'
    ).annotate(total_cost=Sum('cost'))

    vendor_cost_map = {p['vendor_id']: p['total_cost'] for p in purchases_vendor}

    vendor_results = []
    for s in sales_vendor:
        vid = s['product__vendor_id']
        name = s['product__vendor__vendor_name']
        if not name:
            continue
        revenue = float(s['total_revenue'])
        cost = float(vendor_cost_map.get(vid, 0))
        profit = revenue - cost
        margin = (profit / revenue * 100) if revenue > 0 else 0
        vendor_results.append({'name': name.strip(), 'profit': profit, 'margin': margin, 'has_cost': vid in vendor_cost_map})

    top10_vp = sorted(vendor_results, key=lambda x: x['profit'], reverse=True)[:10]
    names_vp = [r['name'] for r in top10_vp]
    profits_vp = [r['profit'] for r in top10_vp]
    margins_vp = [round(r['margin'], 1) for r in top10_vp]

    fig3 = go.Figure(go.Bar(
        x=profits_vp, y=names_vp, orientation='h',
        marker_color='orange',
        text=[f"${p:,.0f} | {m}%" for p, m in zip(profits_vp, margins_vp)],
        textposition='inside',
    ))
    fig3.update_layout(
        title=dict(text='<b>Top 10 Vendors by Profit</b>', x=0.5, xanchor='center'),
        xaxis_title='Profit ($)',
        yaxis=dict(autorange='reversed'),
        margin=dict(l=200, r=20),
    )
    chart_vendor_profit = plot(fig3, output_type='div', include_plotlyjs=False)

    top10_vm = sorted([r for r in vendor_results if r['has_cost']], key=lambda x: x['margin'], reverse=True)[:10]
    names_vm = [r['name'] for r in top10_vm]
    margins_vm = [round(r['margin'], 1) for r in top10_vm]

    fig4 = go.Figure(go.Bar(
        x=margins_vm, y=names_vm, orientation='h',
        marker_color='purple',
        text=[f"{m}%" for m in margins_vm],
        textposition='inside',
    ))
    fig4.update_layout(
        title=dict(text='<b>Top 10 Vendors by Margin</b>', x=0.5, xanchor='center'),
        xaxis_title='Margin (%)',
        yaxis=dict(autorange='reversed'),
        margin=dict(l=200, r=20),
    )
    chart_vendor_margin = plot(fig4, output_type='div', include_plotlyjs=False)

    # Products losing money (profit < 0), sorted by worst margin first, top 50
    losing_products = sorted(
        [r for r in results if r['profit'] < 0],
        key=lambda x: x['margin']
    )[:50]

    context = {
        'chart_profit': chart_profit,
        'chart_margin': chart_margin,
        'chart_vendor_profit': chart_vendor_profit,
        'chart_vendor_margin': chart_vendor_margin,
        'available_years': available_years,
        'months': months,
        'available_cities': available_cities,
        'available_stores': available_stores,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_city': selected_city,
        'selected_store': selected_store,
        'losing_products': losing_products,
    }
    cache.set(cache_key, context, 3600)  # 60 minutos
    return render(request, 'dashboard.html', context)
