import pandas as pd

from django.core.management.base import BaseCommand
from portal.models import Store, Product, Sale


class Command(BaseCommand):
    help = "Load sales data"

    def handle(self, *args, **kwargs):
        file_path = "/app/data/SalesFINAL12312016.csv"

        # Cargamos todo en memoria para no hacer queries por cada fila
        stores_map   = {s.store_id: s.id for s in Store.objects.all()}
        products_map = {p.brand: p.id for p in Product.objects.all()}

        total = 0

        for chunk in pd.read_csv(file_path, chunksize=50000):
            sales = []

            for _, row in chunk.iterrows():
                # "1_HARDERSFIELD_1004" → store_id=1, brand=1004
                parts    = row["InventoryId"].split("_")
                store_id = int(parts[0])
                brand    = int(parts[-1])

                store_pk   = stores_map.get(store_id)
                product_pk = products_map.get(brand)

                if not store_pk or not product_pk:
                    continue  # skip si falta referencia

                sales.append(Sale(
                    store_id=store_pk,
                    product_id=product_pk,
                    quantity=row["SalesQuantity"],
                    revenue=row["SalesDollars"],
                    price=row["SalesPrice"],
                    sales_date=row["SalesDate"],
                ))

            Sale.objects.bulk_create(sales, batch_size=5000)
            total += len(sales)
            self.stdout.write(f"Loaded: {total}")

        self.stdout.write(self.style.SUCCESS(f"Sales total: {total}"))
