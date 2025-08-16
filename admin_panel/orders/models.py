from django.db import models
from django.contrib.auth.models import User
from clients.models import Client

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')

    courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,         #
        null=True, blank=True,
        related_name='assigned_orders',
        help_text="Bu buyurtma uchun mas’ul kurer"
    )

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('completed', 'Bajardi'),
        ('cancelled', 'Bekor qilingan')
    ], default='pending')
    effective_date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
