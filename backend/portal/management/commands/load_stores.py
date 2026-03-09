import pandas as pd

from django.core.management.base import BaseCommand
from portal.models import Store


class Command(BaseCommand):
    help = "Load stores from beginning inventory file"

    def handle(self, *args, **kwargs):
        file_path = "/app/data/BegInvFINAL12312016.csv"
        df = pd.read_csv(file_path)

        # El archivo tiene muchas filas por store, solo necesitamos una por store
        stores_df = df[["Store", "City"]].drop_duplicates()

        stores = []
        for _, row in stores_df.iterrows():
            stores.append(Store(
                store_id=row["Store"],
                city=row["City"],
            ))

        Store.objects.bulk_create(stores, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f"Stores: {len(stores)}"))
