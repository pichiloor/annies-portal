import pandas as pd

from django.core.management.base import BaseCommand
from portal.models import Vendor, Product


class Command(BaseCommand):
    help = "Load vendors and products from purchase price file"

    def handle(self, *args, **kwargs):
        file_path = "/app/data/2017PurchasePricesDec.csv"
        df = pd.read_csv(file_path)

        vendors = {}
        for _, row in df.iterrows():
            vendor, _ = Vendor.objects.get_or_create(
                vendor_number=row["VendorNumber"],
                defaults={"vendor_name": row["VendorName"].strip()},
            )
            vendors[row["VendorNumber"]] = vendor.id

        self.stdout.write(f"Vendors: {len(vendors)}")

        products = []
        for _, row in df.iterrows():
            products.append(Product(
                brand=row["Brand"],
                description=row["Description"],
                size=row["Size"],
                purchase_price=row["PurchasePrice"],
                vendor_id=vendors[row["VendorNumber"]],
            ))

        # For not allow duplicates
        Product.objects.bulk_create(products, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Products: {len(products)}"))
