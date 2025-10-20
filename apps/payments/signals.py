from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order
from apps.payments.models import Payment
from random import randint


@receiver(post_save, sender=Order)
def create_payment_for_order(sender, instance, created, **kwargs):
    if created:
        transaction_id = str(randint(100000, 999999))
        Payment.objects.create(
            order=instance,
            transaction_id=transaction_id,
            amount=instance.total_price,
        )
