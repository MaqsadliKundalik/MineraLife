from django.db import models

class Order(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Karta'),
        ('cash', 'Naqd'),
    ]

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('completed', 'Bajardi'),
        ('cancelled', 'Bekor qilingan'),
    ], default='pending')
    effective_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    # YANGI:
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default='cash',
        help_text="To'lov usuli: Karta yoki Naqd"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
