from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Otp, UserAccount
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging
import random
import string

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserAccount)
def send_otp(sender, instance, created, **kwargs):
    if created and not instance.is_superuser and not instance.source == 'google':
        try:
            # Generate a random 6-digit OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Create OTP
            otp = Otp.objects.create(user=instance, email=instance.email, otp=otp_code, expires_at=timezone.now() + timedelta(minutes=10))
            
            # Prepare email content
            subject = 'Activate Your Account'
            message = render_to_string('activation_email.html', {
                'user': instance,
                'otp': otp.otp,
            })
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [instance.email]
            
            # Send email
            send_mail(subject, message, from_email, to_email, html_message=message)

            # Set account as inactive
            instance.is_active = False
            instance.save(update_fields=['is_active'])

            logger.info(f"Activation email with OTP {otp.otp} sent to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send activation email to {instance.email}: {e}")