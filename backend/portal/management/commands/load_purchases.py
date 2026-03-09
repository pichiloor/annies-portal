import pandas as pd

from django.core.management.base import BaseCommand
from portal.models import Store, Product, Vendor, Purchase


class Command(BaseCommand):
    help = "Load purchases from purchases file"

    def handle(self, *args, **kwargs):
        file_path = "/app/data/PurchasesFINAL12312016.csv"

        # Cargamos todo en memoria para no hacer queries por cada fila
        stores_map   = {s.store_id: s.id for s in Store.objects.all()}
        products_map = {p.brand: p.id for p in Product.objects.all()}
        vendors_map  = {v.vendor_number: v.id for v in Vendor.objects.all()}

        total = 0

        for chunk in pd.read_csv(file_path, chunksize=50000):
            purchases = []

            for _, row in chunk.iterrows():
                # "69_MOUNTMEND_8412" → store_id=69, brand=8412
                parts    = row["InventoryId"].split("_")
                store_id = int(parts[0])
                brand    = int(parts[-1])

                store_pk   = stores_map.get(store_id)
                product_pk = products_map.get(brand)
                vendor_pk  = vendors_map.get(row["VendorNumber"])

                if not store_pk or not product_pk:
                    continue  # skip si falta referencia

                purchases.append(Purchase(
                    store_id=store_pk,
                    product_id=product_pk,
                    vendor_id=vendor_pk,
                    quantity=row["Quantity"],
                    cost=row["Dollars"],
                    purchase_price=row["PurchasePrice"],
                    po_date=row["PODate"] if pd.notna(row["PODate"]) else None,
                ))

            Purchase.objects.bulk_create(purchases, batch_size=5000)
            total += len(purchases)
            self.stdout.write(f"Loaded: {total}")

        self.stdout.write(self.style.SUCCESS(f"Purchases total: {total}"))
