from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Min, Sum
from django.shortcuts import get_object_or_404, redirect, render

from paintings.models import Inquiry, Order, Painting
from .models import Artist


# ── Public: Directory of all Artists ──────────────────────────────
def artist_list(request):
    """Public directory of all master artists catalogued in ArtVault."""
    artists = Artist.objects.annotate(
        works_count=Count('painting')
    ).order_by('name')
    return render(request, 'artists/artist_list.html', {
        'artists': artists,
    })


# ── Public: Artist Detail & Portfolio ─────────────────────────────
def artist_detail(request, pk):
    """Public exhibition portfolio and biography of an artist."""
    artist = get_object_or_404(Artist, pk=pk)
    paintings = artist.painting_set.all().order_by('-year_created')

    stats = paintings.aggregate(
        total_works=Count('id'),
        total_val=Sum('estimated_value'),
        earliest_year=Min('year_created'),
        latest_year=Max('year_created'),
    )

    distinct_styles = list(paintings.values_list('style', flat=True).distinct())

    return render(request, 'artists/artist_detail.html', {
        'artist': artist,
        'paintings': paintings,
        'total_works': stats['total_works'] or 0,
        'total_value': stats['total_val'] or 0,
        'earliest_year': stats['earliest_year'],
        'latest_year': stats['latest_year'],
        'styles': distinct_styles,
    })


# ── Helper: Get artist profile for user ───────────────────────────
def _get_artist_for_user(user):
    if hasattr(user, 'artist_profile') and user.artist_profile is not None:
        return user.artist_profile
    return None


# ── Artist Studio Dashboard ───────────────────────────────────────
@login_required(login_url='/accounts/login/?role=artist')
def artist_dashboard(request):
    """
    Private workspace for artists to manage their artwork inventory,
    upload new pieces, view buyer orders, and track sales commission payouts.
    """
    artist = _get_artist_for_user(request.user)
    if not artist:
        messages.error(request, 'No Artist account found. Please sign in under the Artist / Seller tab.')
        return redirect('/accounts/login/?role=artist')

    # Paintings listed by this artist
    paintings = artist.painting_set.all().order_by('-year_created')

    # Paid sales orders for this artist's works
    orders = (
        Order.objects
        .filter(painting__artist=artist, status='paid')
        .select_related('painting')
        .order_by('-created_at')
    )

    # Inquiries for this artist's works
    inquiries = (
        Inquiry.objects
        .filter(painting__artist=artist)
        .select_related('painting')
        .order_by('-created_at')
    )

    # Financial ledger calculations
    total_sales_val = sum(o.amount for o in orders) if orders else Decimal('0.00')
    total_fees      = sum(o.gallery_fee for o in orders) if orders else Decimal('0.00')
    total_payout    = sum(o.artist_payout for o in orders) if orders else Decimal('0.00')

    context = {
        'artist': artist,
        'paintings': paintings,
        'paintings_count': paintings.count(),
        'available_count': paintings.filter(is_sold=False).count(),
        'sold_count': paintings.filter(is_sold=True).count(),
        'orders': orders,
        'orders_count': orders.count(),
        'inquiries': inquiries,
        'total_sales_val': total_sales_val,
        'total_fees': total_fees,
        'total_payout': total_payout,
    }
    return render(request, 'artists/dashboard.html', context)


# ── Upload & List New Painting ────────────────────────────────────
@login_required(login_url='/accounts/login/?role=artist')
def artist_painting_create(request):
    """Allows an artist to upload and list a new painting into the gallery."""
    artist = _get_artist_for_user(request.user)
    if not artist:
        return redirect('/accounts/login/?role=artist')
    error = None

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        year_created = request.POST.get('year_created', '').strip()
        style        = request.POST.get('style', 'Other')
        materials    = request.POST.get('materials', '').strip()
        dimensions   = request.POST.get('dimensions', '').strip()
        price        = request.POST.get('estimated_value', '').strip()
        story        = request.POST.get('story', '').strip()
        image_file   = request.FILES.get('image')

        if not title:
            error = 'Artwork title is required.'
            messages.error(request, error)
        elif not year_created or not year_created.isdigit():
            error = 'Please enter a valid creation year.'
            messages.error(request, error)
        else:
            val = Decimal(price) if price else None
            p = Painting.objects.create(
                artist=artist,
                title=title,
                year_created=int(year_created),
                style=style,
                materials=materials,
                dimensions=dimensions,
                estimated_value=val,
                story=story,
                image=image_file,
            )
            messages.success(request, f'"{p.title}" has been successfully listed in the ArtVault collection!')
            return redirect('artists:dashboard')

    return render(request, 'artists/painting_form.html', {
        'artist': artist,
        'error': error,
        'action': 'Upload New Artwork',
        'styles': Painting.STYLE_CHOICES,
    })


# ── Edit Painting Listing ─────────────────────────────────────────
@login_required(login_url='/accounts/login/?role=artist')
def artist_painting_edit(request, pk):
    """Allows an artist to update their listed painting."""
    artist = _get_artist_for_user(request.user)
    if not artist:
        return redirect('/accounts/login/?role=artist')
    painting = get_object_or_404(Painting, pk=pk, artist=artist)
    error = None

    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        year_created = request.POST.get('year_created', '').strip()
        style        = request.POST.get('style', 'Other')
        materials    = request.POST.get('materials', '').strip()
        dimensions   = request.POST.get('dimensions', '').strip()
        price        = request.POST.get('estimated_value', '').strip()
        story        = request.POST.get('story', '').strip()
        image_file   = request.FILES.get('image')

        if not title:
            error = 'Artwork title is required.'
            messages.error(request, error)
        elif not year_created or not year_created.isdigit():
            error = 'Please enter a valid creation year.'
            messages.error(request, error)
        else:
            painting.title = title
            painting.year_created = int(year_created)
            painting.style = style
            painting.materials = materials
            painting.dimensions = dimensions
            painting.estimated_value = Decimal(price) if price else None
            painting.story = story
            if image_file:
                painting.image = image_file
            painting.save()

            messages.success(request, f'"{painting.title}" details updated.')
            return redirect('artists:dashboard')

    return render(request, 'artists/painting_form.html', {
        'artist': artist,
        'painting': painting,
        'error': error,
        'action': 'Edit Artwork Details',
        'styles': Painting.STYLE_CHOICES,
    })


# ── Delete Painting Listing ───────────────────────────────────────
@login_required(login_url='/accounts/login/?role=artist')
def artist_painting_delete(request, pk):
    """Delete a painting listing if it has not been acquired yet."""
    artist = _get_artist_for_user(request.user)
    if not artist:
        return redirect('/accounts/login/?role=artist')
    painting = get_object_or_404(Painting, pk=pk, artist=artist)

    if request.method == 'POST':
        if painting.is_sold or painting.orders.filter(status='paid').exists():
            messages.error(request, 'Cannot delete an artwork that has already been acquired by a collector.')
        else:
            title = painting.title
            painting.delete()
            messages.success(request, f'"{title}" listing removed from collection.')
        return redirect('artists:dashboard')

    return render(request, 'artists/painting_confirm_delete.html', {
        'painting': painting,
        'artist': artist,
    })


# ── Artist Profile & Payout Settings ──────────────────────────────
@login_required(login_url='/accounts/login/?role=artist')
def artist_profile_edit(request):
    """Edit artist public biography, photo, and payout credentials."""
    artist = _get_artist_for_user(request.user)
    if not artist:
        return redirect('/accounts/login/?role=artist')

    if request.method == 'POST':
        name            = request.POST.get('name', '').strip()
        birth_year      = request.POST.get('birth_year', '').strip()
        bio             = request.POST.get('bio', '').strip()
        payout_upi_id   = request.POST.get('payout_upi_id', '').strip()
        bank_details    = request.POST.get('payout_bank_details', '').strip()
        photo_file      = request.FILES.get('photo')

        if name:
            artist.name = name
        artist.birth_year = int(birth_year) if birth_year.isdigit() else None
        artist.bio = bio
        artist.payout_upi_id = payout_upi_id
        artist.payout_bank_details = bank_details
        if photo_file:
            artist.photo = photo_file
        artist.save()

        messages.success(request, 'Your artist profile and payout settings have been saved.')
        return redirect('artists:dashboard')

    return render(request, 'artists/profile_form.html', {
        'artist': artist,
    })
