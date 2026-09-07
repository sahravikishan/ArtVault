from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from artists.models import Artist
from paintings.models import Order, Painting
from .models import CollectorProfile, Favourite


# ── Register (Collector vs Artist / Seller) ──────────────────────
def register_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'artist_profile') and request.user.artist_profile:
            return redirect('artists:dashboard')
        return redirect('accounts:vault')

    error = None
    active_role = request.GET.get('role', 'user')
    name = ''
    email = ''
    bio = ''
    birth_year = ''

    if request.method == 'POST':
        active_role = request.POST.get('role', 'user')
        email       = request.POST.get('email', '').strip().lower()
        password    = request.POST.get('password', '')
        confirm     = request.POST.get('confirm', '')
        name        = request.POST.get('name', '').strip()
        bio         = request.POST.get('bio', '').strip()
        birth_year  = request.POST.get('birth_year', '').strip()

        if not all([email, password, confirm, name]):
            error = 'Please fill in your name, email, and password.'
            messages.error(request, error)
        elif password != confirm:
            error = 'Passwords do not match.'
            messages.error(request, error)
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
            messages.error(request, error)
        else:
            existing_user = User.objects.filter(email__iexact=email).first()
            if not existing_user:
                existing_user = User.objects.filter(username__iexact=email).first()

            if active_role == 'artist':
                # Registering as Artist / Seller
                if existing_user and hasattr(existing_user, 'artist_profile') and existing_user.artist_profile:
                    error = 'An Artist account is already registered with this email address. Please sign in to your Artist Studio.'
                    messages.error(request, error)
                elif existing_user:
                    # User exists as Collector; create linked Artist account with same name & email
                    b_year = int(birth_year) if birth_year.isdigit() else None
                    artist = Artist.objects.create(
                        user=existing_user,
                        name=name,
                        bio=bio,
                        birth_year=b_year,
                    )
                    # Establish relationship to existing CollectorProfile
                    if hasattr(existing_user, 'collector_profile') and existing_user.collector_profile:
                        existing_user.collector_profile.linked_artist = artist
                        existing_user.collector_profile.save()

                    login(request, existing_user)
                    request.session['active_role'] = 'artist'
                    messages.success(request, f"Welcome to ArtVault Studio, {name}! Your Artist Studio has been established and linked to your collector profile.")
                    return redirect('artists:dashboard')
                else:
                    first_name = name.split()[0]
                    last_name  = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    b_year = int(birth_year) if birth_year.isdigit() else None
                    Artist.objects.create(
                        user=user,
                        name=name,
                        bio=bio,
                        birth_year=b_year,
                    )
                    login(request, user)
                    request.session['active_role'] = 'artist'
                    messages.success(request, f"Welcome to ArtVault Studio, {name}! Your Artist Studio is ready.")
                    return redirect('artists:dashboard')
            else:
                # Registering as Collector / Buyer
                if existing_user and hasattr(existing_user, 'collector_profile') and existing_user.collector_profile:
                    error = 'A Collector account is already registered with this email address. Please sign in.'
                    messages.error(request, error)
                elif existing_user:
                    # User exists as Artist; create linked Collector account with same name & email
                    collector = CollectorProfile.objects.create(
                        user=existing_user,
                        name=name,
                        email=email,
                        linked_artist=existing_user.artist_profile if hasattr(existing_user, 'artist_profile') else None,
                    )
                    login(request, existing_user)
                    request.session['active_role'] = 'user'
                    messages.success(request, f"Welcome to ArtVault, {name}! Your Collector account has been created and linked to your artist studio.")
                    return redirect('accounts:vault')
                else:
                    first_name = name.split()[0]
                    last_name  = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    CollectorProfile.objects.create(
                        user=user,
                        name=name,
                        email=email,
                    )
                    login(request, user)
                    request.session['active_role'] = 'user'
                    messages.success(request, f"Welcome to ArtVault, {name}! Your private collector vault has been established.")
                    return redirect('accounts:vault')

    return render(request, 'accounts/register.html', {
        'error': error,
        'active_role': active_role,
        'name': name,
        'email': email,
        'bio': bio,
        'birth_year': birth_year,
    })


# ── Login (Collector vs Artist / Seller) ──────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'artist_profile') and request.user.artist_profile:
            return redirect('artists:dashboard')
        return redirect('accounts:vault')

    error = None
    active_role = request.GET.get('role', 'user')
    identifier = ''

    if request.method == 'POST':
        active_role = request.POST.get('role', 'user')
        identifier  = request.POST.get('login_id', '').strip()
        password    = request.POST.get('password', '')

        # Resolve username if entered as email
        target_username = identifier
        user_by_email = User.objects.filter(email__iexact=identifier).first()
        if user_by_email:
            target_username = user_by_email.username

        user = authenticate(request, username=target_username, password=password)

        if user is not None:
            if active_role == 'artist':
                # Strictly enforce Artist role
                if not hasattr(user, 'artist_profile') or user.artist_profile is None:
                    if hasattr(user, 'collector_profile') and user.collector_profile is not None:
                        error = 'This account is registered as a Collector / Buyer. Please select the "Collector / Buyer" tab to sign in, or register an Artist account to access the Artist Studio.'
                    else:
                        error = 'No Artist account found with these credentials. Please register an Artist account.'
                    messages.error(request, error)
                else:
                    login(request, user)
                    request.session['active_role'] = 'artist'
                    artist_name = user.artist_profile.name if user.artist_profile and user.artist_profile.name else (user.first_name or user.username)
                    messages.success(request, f"Welcome back, {artist_name}! Signed into your Artist Studio.")
                    return redirect('artists:dashboard')
            else:
                # Strictly enforce Collector role
                if not hasattr(user, 'collector_profile') or user.collector_profile is None:
                    if hasattr(user, 'artist_profile') and user.artist_profile is not None:
                        error = 'This account is registered as an Artist / Seller. Please select the "Artist / Seller" tab to enter your Artist Studio, or create a Collector account.'
                    else:
                        error = 'No Collector account found with these credentials. Please create a Collector account.'
                    messages.error(request, error)
                else:
                    login(request, user)
                    request.session['active_role'] = 'user'
                    collector_name = user.collector_profile.name if user.collector_profile and user.collector_profile.name else (user.first_name or user.username)
                    messages.success(request, f"Welcome back, {collector_name}! Signed into your Collector Vault.")
                    next_url = request.GET.get('next', '')
                    return redirect(next_url if next_url else 'accounts:vault')
        else:
            error = 'Invalid email or password. Please verify your credentials and selected role.'
            messages.error(request, error)

    return render(request, 'accounts/login.html', {
        'error': error,
        'active_role': active_role,
        'login_id': identifier,
    })


# ── Logout ────────────────────────────────────────────────────────
@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out of ArtVault.")
    return redirect('paintings:home')


# ── My Vault dashboard (Collector) ────────────────────────────────
@login_required(login_url='/accounts/login/')
def vault_view(request):
    if not hasattr(request.user, 'collector_profile') or request.user.collector_profile is None:
        if hasattr(request.user, 'artist_profile') and request.user.artist_profile is not None:
            return redirect('artists:dashboard')

    favourites = (
        Favourite.objects
        .filter(user=request.user)
        .select_related('painting', 'painting__artist')
    )
    orders = (
        Order.objects
        .filter(buyer_email=request.user.email, status='paid')
        .select_related('painting', 'painting__artist')
    )
    return render(request, 'accounts/vault.html', {
        'favourites': favourites,
        'orders': orders,
    })


# ── Toggle Favourite (AJAX) ───────────────────────────────────────
@login_required(login_url='/accounts/login/')
@require_POST
def toggle_favourite(request, pk):
    painting = get_object_or_404(Painting, pk=pk)
    fav, created = Favourite.objects.get_or_create(user=request.user, painting=painting)
    if not created:
        fav.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'saved'})
