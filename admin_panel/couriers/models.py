from django.db import models
from django.contrib.auth.models import User


class CourierRoute(models.Model):
    """Kuryerning kunlik marshrutini saqlash"""
    courier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='routes',
        verbose_name="Kuryer"
    )
    date = models.DateField(verbose_name="Sana")
    route_data = models.JSONField(
        verbose_name="Marshrut ma'lumotlari",
        help_text="Marshrut koordinatalari va tartib",
        default=list
    )
    color = models.CharField(
        max_length=7,
        default="#2563eb",
        verbose_name="Marshrut rangi",
        help_text="Hex format: #RRGGBB"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kuryer marshruty"
        verbose_name_plural = "Kuryer marshrutlari"
        unique_together = ('courier', 'date')
        ordering = ['-date', 'courier__username']

    def __str__(self):
        return f"{self.courier.username} - {self.date}"
