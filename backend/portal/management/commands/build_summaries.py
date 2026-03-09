from django.core.management.base import BaseCommand
from django.db.models import Sum
from portal.models import Sale, Purchase, SaleSummary, PurchaseSummary


class Command(BaseCommand):
    help = "Rebuild sale and purchase summary tables"

    def handle(self, *args, **kwargs):
        self.stdout.write("Building sale summaries...")
        SaleSummary.objects.all().delete()

        sales = (
            Sale.objects
            .values(
                'store_id', 'store__store_id', 'store__city',
                'product_id', 'product__brand', 'product__description',
                'product__vendor_id', 'product__vendor__vendor_name',
                'sales_date__year', 'sales_date__month',
            )
            .annotate(
                total_revenue=Sum('revenue'),
                total_qty_sold=Sum('quantity'),
            )
        )

        SaleSummary.objects.bulk_create([
            SaleSummary(
                store_id=r['store__store_id'],
                city=r['store__city'],
                product_id=r['product__brand'],
                description=r['product__description'],
                vendor_id=r['product__vendor_id'] or 0,
                vendor_name=r['product__vendor__vendor_name'] or '',
                year=r['sales_date__year'],
                month=r['sales_date__month'],
                total_revenue=r['total_revenue'],
                total_qty_sold=r['total_qty_sold'],
            )
            for r in sales
        ], batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"Sale summaries: {SaleSummary.objects.count()}"))

        self.stdout.write("Building purchase summaries...")
        PurchaseSummary.objects.all().delete()

        purchases = (
            Purchase.objects
            .values(
                'store_id', 'store__store_id', 'store__city',
                'product_id', 'product__brand', 'product__description',
                'vendor_id', 'vendor__vendor_name',
                'po_date__year', 'po_date__month',
            )
            .annotate(
                total_cost=Sum('cost'),
                total_qty_bought=Sum('quantity'),
            )
        )

        PurchaseSummary.objects.bulk_create([
            PurchaseSummary(
                store_id=r['store__store_id'],
                city=r['store__city'],
                product_id=r['product__brand'],
                description=r['product__description'],
                vendor_id=r['vendor_id'] or 0,
                vendor_name=r['vendor__vendor_name'] or '',
                year=r['po_date__year'],
                month=r['po_date__month'],
                total_cost=r['total_cost'],
                total_qty_bought=r['total_qty_bought'],
            )
            for r in purchases
            if r['po_date__year'] is not None
        ], batch_size=5000)
        self.stdout.write(self.style.SUCCESS(f"Purchase summaries: {PurchaseSummary.objects.count()}"))
