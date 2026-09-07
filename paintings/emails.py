"""
paintings/emails.py
Handles all outbound emails triggered by painting acquisition events.
"""
import logging
import sys

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .templatetags.currency_tags import inr

logger = logging.getLogger(__name__)

# Ensure console output doesn't crash on Windows with UTF-8 characters like ₹
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def send_acquisition_emails(order):
    """
    Send two emails on a successful acquisition:
      1. A beautiful HTML confirmation to the buyer.
      2. A plain-text alert to the ArtVault admin.

    Both are fire-and-forget — failures are logged but never
    propagate to the caller so the user still sees the success page.
    """
    context = {
        'order':            order,
        'amount_formatted': inr(order.amount),
    }

    # ── 1. Buyer HTML confirmation ────────────────────────────────
    try:
        subject    = f'Your Acquisition — {order.painting.title} | ArtVault'
        html_body  = render_to_string('emails/acquisition_buyer.html', context)
        # Plain-text fallback
        text_body  = (
            f"Dear {order.buyer_name},\n\n"
            f"Your acquisition of '{order.painting.title}' "
            f"by {order.painting.artist.name} has been confirmed.\n\n"
            f"Order Reference : #{order.pk}\n"
            f"Payment ID      : {order.razorpay_payment_id}\n"
            f"Amount Paid     : {inr(order.amount)}\n\n"
            f"Thank you for growing your collection with ArtVault."
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.buyer_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        logger.info('Acquisition confirmation sent to %s', order.buyer_email)

    except Exception:
        logger.exception(
            'Failed to send buyer confirmation for order #%s', order.pk
        )

    # ── 2. Admin plain-text alert ─────────────────────────────────
    admin_email = getattr(settings, 'ARTVAULT_ADMIN_EMAIL', '')
    if not admin_email:
        return   # No admin email configured — skip silently

    try:
        admin_subject = (
            f'[ArtVault] New Acquisition — {order.painting.title} '
            f'by {order.buyer_name}'
        )
        admin_body = render_to_string('emails/acquisition_admin.txt', context)
        EmailMultiAlternatives(
            subject=admin_subject,
            body=admin_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        ).send()
        logger.info('Admin acquisition alert sent to %s', admin_email)

    except Exception:
        logger.exception(
            'Failed to send admin alert for order #%s', order.pk
        )
