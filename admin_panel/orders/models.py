from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Order(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Karta'),
        ('cash', 'Naqd'),
        ("perechesleniya", "Perechesleniya"),
    ]

    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    inquantity = models.PositiveIntegerField(default=0)
    outquantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=17000.00, help_text="Bir dona uchun narx")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Kutilmoqda'),
        ('completed', 'Bajardi'),
        ('cancelled', 'Bekor qilingan'),
    ], default='pending')
    effective_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    # YANGI:
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        help_text="To'lov usuli: Karta yoki Naqd"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
    
    def __str__(self):
        return f"#{self.id} - {self.client.name} ({self.get_status_display()})"
    
    def get_total_price(self):
        """Umumiy narx: berdim miqdor * birlik narx"""
        return self.outquantity * self.price
    
    def get_price_display(self):
        """Narxni ko'rsatish uchun"""
        if self.outquantity > 0:
            return f"{self.get_total_price():,.0f} so'm ({self.outquantity} x {self.price:,.0f})"
        return f"{self.price:,.0f} so'm"
    
    def save(self, *args, **kwargs):
        """Saqlashdan oldin narxni hisoblash mumkin"""
        # Agar kerak bo'lsa, price ni avtomatik yangilash mumkin
        super().save(*args, **kwargs)
    

