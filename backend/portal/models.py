from django.db import models


class Vendor(models.Model):
    vendor_number = models.IntegerField(unique=True)
    vendor_name = models.CharField(max_length=255)

    def __str__(self):
        return self.vendor_name


class Product(models.Model):
    brand = models.IntegerField(unique=True)
    description = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.description


class Store(models.Model):
    store_id = models.IntegerField(unique=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.city


class Sale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sales_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=["sales_date"]),
            models.Index(fields=["store", "sales_date"]),
            models.Index(fields=["product", "sales_date"]),
        ]

    def __str__(self):
        return f"{self.product} - {self.sales_date}"


class Purchase(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    po_date = models.DateField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=["po_date"]),
            models.Index(fields=["store", "po_date"]),
            models.Index(fields=["product", "po_date"]),
            models.Index(fields=["vendor", "po_date"]),
        ]

    def __str__(self):
        return f"{self.product} - {self.cost}"

class SaleSummary(models.Model):
    store_id    = models.IntegerField()
    city        = models.CharField(max_length=100)
    product_id  = models.IntegerField()
    description = models.CharField(max_length=255)
    vendor_id   = models.IntegerField()
    vendor_name = models.CharField(max_length=255)
    year        = models.IntegerField()
    month       = models.IntegerField()
    total_revenue   = models.DecimalField(max_digits=14, decimal_places=2)
    total_qty_sold  = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['store_id', 'year', 'month']),
            models.Index(fields=['city', 'year', 'month']),
        ]


class PurchaseSummary(models.Model):
    store_id    = models.IntegerField()
    city        = models.CharField(max_length=100)
    product_id  = models.IntegerField()
    description = models.CharField(max_length=255)
    vendor_id   = models.IntegerField()
    vendor_name = models.CharField(max_length=255)
    year        = models.IntegerField()
    month       = models.IntegerField()
    total_cost       = models.DecimalField(max_digits=14, decimal_places=2)
    total_qty_bought = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['year', 'month']),
            models.Index(fields=['store_id', 'year', 'month']),
            models.Index(fields=['city', 'year', 'month']),
        ]
