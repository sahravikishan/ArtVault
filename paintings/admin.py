from django.contrib import admin
from django.utils.html import format_html
from .models import Painting, Order, Exhibition, Inquiry
from .templatetags.currency_tags import inr


# ── Custom Image Preview Widget ───────────────────────────────────
class ImagePreviewMixin:
    """Adds a live image preview thumbnail in the Django Admin change form."""

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin:8px 0;">'
                '<img src="{}" style="max-height:220px; max-width:100%; '
                'border:1px solid #ddd; border-radius:4px; object-fit:cover;" />'
                '</div>',
                obj.image.url,
            )
        return format_html(
            '<p style="color:#999; font-style:italic;">No image uploaded yet.</p>'
        )

    image_preview.short_description = 'Current Image'


# ── Painting Admin ─────────────────────────────────────────────────
@admin.register(Painting)
class PaintingAdmin(ImagePreviewMixin, admin.ModelAdmin):
    # List view
    list_display   = ('thumb', 'title', 'artist', 'year_created', 'style', 'formatted_value', 'is_sold', 'has_image')
    list_display_links = ('thumb', 'title')
    search_fields  = ('title', 'artist__name', 'story', 'materials')
    list_filter    = ('is_sold', 'style', 'year_created', 'artist')
    list_per_page  = 20

    # Change form — group fields into logical sections
    fieldsets = (
        ('Core Details', {
            'fields': ('title', 'artist', 'year_created', 'style'),
        }),
        ('Image', {
            'fields': ('image_preview', 'image'),
            'description': 'Upload a high-resolution JPEG or PNG. The image will be displayed '
                           'on the collection grid and the painting detail page.',
        }),
        ('Description', {
            'fields': ('story', 'materials', 'dimensions'),
        }),
        ('Provenance & Value', {
            'fields': ('current_location', 'estimated_value'),
        }),
    )

    readonly_fields = ('image_preview',)

    # ── Custom list columns ──────────────────────────────────────
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:48px; width:48px; object-fit:cover; '
                'border-radius:4px; border:1px solid #ddd;" />',
                obj.image.url,
            )
        return format_html(
            '<div style="height:48px;width:48px;background:#f5f5f5;border:1px solid #ddd;'
            'border-radius:4px;display:flex;align-items:center;justify-content:center;'
            'color:#bbb;font-size:18px;">🖼</div>'
        )
    thumb.short_description = ''

    def has_image(self, obj):
        if obj.image:
            return format_html('<span style="color:#2e7d32;">✔ Yes</span>')
        return format_html('<span style="color:#c62828;">✘ No</span>')
    has_image.short_description = 'Image'

    def formatted_value(self, obj):
        return inr(obj.estimated_value)
    formatted_value.short_description = 'Estimated Value'


# ── Artist Admin ──────────────────────────────────────────────────
from artists.models import Artist

@admin.register(Artist)
class ArtistAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display   = ('artist_thumb', 'name', 'birth_year', 'has_photo', 'painting_count')
    list_display_links = ('artist_thumb', 'name')
    search_fields  = ('name', 'bio')
    list_per_page  = 20

    fieldsets = (
        ('Artist Info', {
            'fields': ('name', 'birth_year', 'bio'),
        }),
        ('Photo', {
            'fields': ('image_preview', 'photo'),
            'description': 'Upload a portrait or profile image for the artist.',
        }),
    )

    readonly_fields = ('image_preview',)

    # Override image_preview for Artist (uses 'photo' field, not 'image')
    def image_preview(self, obj):
        if obj.photo:
            return format_html(
                '<div style="margin:8px 0;">'
                '<img src="{}" style="max-height:220px; max-width:300px; '
                'border:1px solid #ddd; border-radius:4px; object-fit:cover;" />'
                '</div>',
                obj.photo.url,
            )
        return format_html(
            '<p style="color:#999; font-style:italic;">No photo uploaded yet.</p>'
        )
    image_preview.short_description = 'Current Photo'

    def artist_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:48px; width:48px; object-fit:cover; '
                'border-radius:50%; border:1px solid #ddd;" />',
                obj.photo.url,
            )
        return format_html(
            '<div style="height:48px;width:48px;background:#f5f5f5;border:1px solid #ddd;'
            'border-radius:50%;display:flex;align-items:center;justify-content:center;'
            'color:#bbb;font-size:18px;">👤</div>'
        )
    artist_thumb.short_description = ''

    def has_photo(self, obj):
        if obj.photo:
            return format_html('<span style="color:#2e7d32;">✔ Yes</span>')
        return format_html('<span style="color:#c62828;">✘ No</span>')
    has_photo.short_description = 'Photo'

    def painting_count(self, obj):
        count = obj.painting_set.count()
        return format_html(
            '<a href="/admin/paintings/painting/?artist__id__exact={}">{} painting{}</a>',
            obj.pk, count, 's' if count != 1 else ''
        )
    painting_count.short_description = 'Paintings'


# ── Order Admin ───────────────────────────────────────────────────
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'painting_thumb', 'painting', 'buyer_name', 'sale_type',
                     'buyer_email', 'formatted_amount', 'formatted_fee', 'formatted_payout', 'status_badge', 'created_at')
    list_filter   = ('sale_type', 'status', 'created_at')
    search_fields = ('buyer_name', 'buyer_email', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = (
        'painting', 'buyer_name', 'buyer_email', 'buyer_phone',
        'sale_type', 'fee_percentage', 'amount', 'gallery_fee', 'artist_payout',
        'razorpay_order_id', 'razorpay_payment_id',
        'razorpay_signature', 'created_at',
    )
    ordering = ('-created_at',)

    def painting_thumb(self, obj):
        if obj.painting.image:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;object-fit:cover;'
                'border-radius:3px;border:1px solid #ddd;" />',
                obj.painting.image.url,
            )
        return '—'
    painting_thumb.short_description = ''

    def formatted_amount(self, obj):
        return inr(obj.amount)
    formatted_amount.short_description = 'Gross Sale'

    def formatted_fee(self, obj):
        fee_str = inr(obj.gallery_fee)
        pct = obj.fee_percentage
        return format_html('{} <span style="font-size:0.75rem;color:#888;">({}%)</span>', fee_str, pct)
    formatted_fee.short_description = 'Gallery Cut'

    def formatted_payout(self, obj):
        return inr(obj.artist_payout)
    formatted_payout.short_description = 'Artist Payout'

    def status_badge(self, obj):
        colours = {'paid': '#2e7d32', 'pending': '#e65100', 'failed': '#c62828'}
        colour  = colours.get(obj.status, '#666')
        return format_html(
            '<span style="color:{};font-weight:600;text-transform:uppercase;'
            'font-size:0.75rem;letter-spacing:0.05em;">{}</span>',
            colour, obj.status,
        )
    status_badge.short_description = 'Status'


# ── Exhibition Admin ──────────────────────────────────────────────
@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'curator_name', 'commission_rate', 'is_ongoing', 'featured', 'start_date', 'end_date', 'paintings_count')
    list_filter = ('is_ongoing', 'featured', 'start_date')
    search_fields = ('title', 'subtitle', 'curator_statement', 'curator_name')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('paintings',)

    def paintings_count(self, obj):
        return obj.paintings.count()
    paintings_count.short_description = 'Works'


# ── Inquiry Admin ─────────────────────────────────────────────────
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'collector_name', 'collector_email', 'inquiry_type', 'painting', 'preferred_date', 'status', 'created_at')
    list_filter = ('inquiry_type', 'status', 'created_at')
    search_fields = ('collector_name', 'collector_email', 'collector_phone', 'message', 'painting__title')
    list_editable = ('status',)
    readonly_fields = ('painting', 'collector_name', 'collector_email', 'collector_phone', 'inquiry_type', 'preferred_date', 'message', 'created_at')
