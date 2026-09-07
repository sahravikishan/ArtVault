import hashlib
import hmac
import json
import logging

import razorpay
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .emails import send_acquisition_emails
from .models import Order, Painting, Exhibition, Inquiry

logger = logging.getLogger(__name__)


# ── Helper: Razorpay client ──────────────────────────────────────
def _razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ── View 1: Home / Collection listing ───────────────────────────
def home(request):
    style_filter = request.GET.get('style', '')
    query        = request.GET.get('q', '').strip()

    paintings = Painting.objects.select_related('artist').all()

    # Style filter
    if style_filter:
        paintings = paintings.filter(style=style_filter)

    # Keyword search — title, artist name, story, materials
    if query:
        paintings = paintings.filter(
            Q(title__icontains=query)
            | Q(artist__name__icontains=query)
            | Q(story__icontains=query)
            | Q(materials__icontains=query)
            | Q(style__icontains=query)
        ).distinct()

    style_choices = Painting.STYLE_CHOICES

    return render(request, 'paintings/home.html', {
        'paintings':     paintings,
        'style_choices': style_choices,
        'active_style':  style_filter,
        'query':         query,
    })


# ── View 2: Painting detail ──────────────────────────────────────
def painting_detail(request, pk):
    painting = get_object_or_404(
        Painting.objects.select_related('artist'), pk=pk
    )
    is_favourite = False
    if request.user.is_authenticated:
        from accounts.models import Favourite
        is_favourite = Favourite.objects.filter(
            user=request.user, painting=painting
        ).exists()
    return render(request, 'paintings/painting_detail.html', {
        'painting': painting,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'is_favourite': is_favourite,
    })


# ── View 3: Initiate payment (AJAX POST) ─────────────────────────
def initiate_payment(request, pk):
    """
    Called when the buyer clicks "Acquire This Work".
    Creates a Razorpay order and saves a pending Order record.
    Returns JSON { order_id, amount, currency, key_id }.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    painting = get_object_or_404(Painting, pk=pk)

    if not painting.estimated_value:
        return JsonResponse({'error': 'This painting has no price set.'}, status=400)

    try:
        body = json.loads(request.body)
        buyer_name  = body.get('name', '').strip()
        buyer_email = body.get('email', '').strip()
        buyer_phone = body.get('phone', '').strip()

        if not all([buyer_name, buyer_email, buyer_phone]):
            return JsonResponse({'error': 'Name, email, and phone are required.'}, status=400)

        # Razorpay expects amount in paise (1 INR = 100 paise)
        amount_paise = int(painting.estimated_value * 100)

        client = _razorpay_client()
        rz_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f'artvault_painting_{painting.pk}',
            'notes': {
                'painting_title': painting.title,
                'buyer_name': buyer_name,
                'buyer_email': buyer_email,
            },
        })

        # Determine sale type & fee percentage: 5% normal, 7-8% exhibition auction
        is_exh = painting.exhibitions.exists()
        sale_type = 'exhibition' if is_exh else 'normal'
        if is_exh:
            exh = painting.exhibitions.first()
            fee_pct = exh.commission_rate if (exh and exh.commission_rate) else 7.50
        else:
            fee_pct = 5.00

        # Persist a pending order
        order = Order.objects.create(
            painting=painting,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_phone=buyer_phone,
            amount=painting.estimated_value,
            sale_type=sale_type,
            fee_percentage=fee_pct,
            razorpay_order_id=rz_order['id'],
            status='pending',
        )

        return JsonResponse({
            'order_id':   rz_order['id'],
            'amount':     amount_paise,
            'currency':   'INR',
            'key_id':     settings.RAZORPAY_KEY_ID,
            'db_order_pk': order.pk,
            'painting_title': painting.title,
            'buyer_name':  buyer_name,
            'buyer_email': buyer_email,
            'buyer_phone': buyer_phone,
        })

    except razorpay.errors.BadRequestError as exc:
        logger.error('Razorpay BadRequest: %s', exc)
        return JsonResponse({'error': str(exc)}, status=400)
    except Exception as exc:
        logger.exception('Razorpay order creation failed')
        return JsonResponse({'error': 'Could not create payment order. Please try again.'}, status=500)


# ── View 4: Verify payment signature (POST from Razorpay JS SDK) ─
@csrf_exempt          # Razorpay posts here without Django's CSRF token
def verify_payment(request):
    """
    After the user completes payment in the Razorpay popup, their browser
    POSTs the three Razorpay fields here. We verify the HMAC-SHA256
    signature and mark the order as paid.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body)
        razorpay_order_id   = body['razorpay_order_id']
        razorpay_payment_id = body['razorpay_payment_id']
        razorpay_signature  = body['razorpay_signature']

        # Fetch the pending order
        order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)

        # Verify signature: HMAC-SHA256(order_id + "|" + payment_id, secret)
        expected_sig = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(expected_sig, razorpay_signature):
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature  = razorpay_signature
            order.status              = 'paid'
            order.save()

            # Mark painting as sold in gallery catalog
            order.painting.is_sold = True
            order.painting.save()

            # Dispatch acquisition confirmation emails (buyer + admin)
            send_acquisition_emails(order)

            return JsonResponse({
                'status': 'ok',
                'redirect': f'/payment/success/{order.pk}/',
            })
        else:
            order.status = 'failed'
            order.save()
            return JsonResponse({'status': 'error', 'error': 'Signature mismatch'}, status=400)

    except Exception as exc:
        logger.exception('Payment verification failed')
        return JsonResponse({'error': str(exc)}, status=500)


# ── View 5: Order success page ───────────────────────────────────
def order_success(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk, status='paid')
    return render(request, 'paintings/order_success.html', {'order': order})


# ── View 6: Certificate of Authenticity (COA) ────────────────────
def certificate_view(request, order_pk):
    order = get_object_or_404(
        Order.objects.select_related('painting', 'painting__artist'),
        pk=order_pk,
        status='paid'
    )
    return render(request, 'paintings/certificate.html', {
        'order': order,
        'certificate_number': order.certificate_number,
    })


# ── View 7: Exhibitions Directory ────────────────────────────────
def exhibition_list(request):
    ongoing_exhibitions = Exhibition.objects.filter(is_ongoing=True).prefetch_related('paintings')
    past_exhibitions = Exhibition.objects.filter(is_ongoing=False).prefetch_related('paintings')
    return render(request, 'paintings/exhibition_list.html', {
        'ongoing_exhibitions': ongoing_exhibitions,
        'past_exhibitions': past_exhibitions,
    })


# ── View 8: Exhibition Detail & Catalogued Works ─────────────────
def exhibition_detail(request, slug):
    exhibition = get_object_or_404(
        Exhibition.objects.prefetch_related('paintings__artist'),
        slug=slug
    )
    paintings = exhibition.paintings.all().select_related('artist')
    artists = list({p.artist for p in paintings})
    return render(request, 'paintings/exhibition_detail.html', {
        'exhibition': exhibition,
        'paintings': paintings,
        'artists': artists,
    })


# ── View 9: Submit Collector Inquiry / Book Private Viewing ──────
@csrf_exempt
def inquire_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    painting = get_object_or_404(Painting, pk=pk)

    try:
        body = json.loads(request.body)
        collector_name  = body.get('name', '').strip()
        collector_email = body.get('email', '').strip()
        collector_phone = body.get('phone', '').strip()
        inquiry_type    = body.get('inquiry_type', 'private_viewing')
        preferred_date  = body.get('preferred_date', None) or None
        message         = body.get('message', '').strip()

        if not collector_name or not collector_email:
            return JsonResponse({'error': 'Name and Email are required.'}, status=400)

        Inquiry.objects.create(
            painting=painting,
            collector_name=collector_name,
            collector_email=collector_email,
            collector_phone=collector_phone,
            inquiry_type=inquiry_type,
            preferred_date=preferred_date,
            message=message,
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Thank you, {collector_name}. Your curatorial inquiry for "{painting.title}" has been registered. Our Chief Curator will contact you shortly.',
        })
    except Exception as exc:
        logger.exception('Inquiry creation failed')
        return JsonResponse({'error': 'Unable to process inquiry. Please try again.'}, status=500)
