from django.db import models
from artists.models import Artist


class Painting(models.Model):
    STYLE_CHOICES = [
        ('Realism', 'Realism'),
        ('Impressionism', 'Impressionism'),
        ('Abstract', 'Abstract'),
        ('Surrealism', 'Surrealism'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=300)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    year_created = models.IntegerField()
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='Other')
    story = models.TextField(blank=True)
    materials = models.CharField(max_length=300, blank=True)
    dimensions = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=300, blank=True, null=True)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='paintings/', blank=True, null=True)
    is_sold = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year_created']

    def __str__(self):
        return f'{self.title} ({self.year_created})'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    painting            = models.ForeignKey(Painting, on_delete=models.PROTECT, related_name='orders')
    buyer_name          = models.CharField(max_length=200)
    buyer_email         = models.EmailField()
    buyer_phone         = models.CharField(max_length=20)
    amount              = models.DecimalField(max_digits=12, decimal_places=2)

    # Commission calculations: 5% normal selling, 7-8% exhibition / auction selling
    SALE_TYPE_CHOICES = [
        ('normal', 'Normal Gallery Sale (5%)'),
        ('exhibition', 'Exhibition Auction Sale (7-8%)'),
    ]
    sale_type           = models.CharField(max_length=20, choices=SALE_TYPE_CHOICES, default='normal')
    fee_percentage      = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    gallery_fee         = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    artist_payout       = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Razorpay IDs
    razorpay_order_id   = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature  = models.CharField(max_length=300, blank=True)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def certificate_number(self):
        year = self.created_at.year if self.created_at else 2026
        return f"AV-COA-{year}-{self.pk:05d}"

    def save(self, *args, **kwargs):
        if self.status == 'paid' and self.amount and not self.gallery_fee:
            from decimal import Decimal
            amt = Decimal(str(self.amount))

            # Determine whether this is an exhibition auction or normal sale
            is_exhibition = (
                self.sale_type == 'exhibition' or
                (self.painting_id and self.painting.exhibitions.exists())
            )

            if is_exhibition:
                self.sale_type = 'exhibition'
                exh = self.painting.exhibitions.first() if self.painting_id else None
                if exh and hasattr(exh, 'commission_rate') and exh.commission_rate:
                    self.fee_percentage = Decimal(str(exh.commission_rate))
                elif not self.fee_percentage or self.fee_percentage == Decimal('5.00') or self.fee_percentage == Decimal('15.00'):
                    self.fee_percentage = Decimal('7.50')  # 7-8% exhibition auction rate (7.5%)
            else:
                self.sale_type = 'normal'
                if not self.fee_percentage or self.fee_percentage == Decimal('15.00') or self.fee_percentage == Decimal('7.50'):
                    self.fee_percentage = Decimal('5.00')  # 5% normal selling rate

            fee_pct_dec = Decimal(str(self.fee_percentage))
            rate = fee_pct_dec / Decimal('100.0')
            self.gallery_fee = round(amt * rate, 2)
            self.artist_payout = round(amt - self.gallery_fee, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order #{self.pk} — {self.painting.title} ({self.status})'


class Exhibition(models.Model):
    title               = models.CharField(max_length=250)
    slug                = models.SlugField(max_length=250, unique=True)
    subtitle            = models.CharField(max_length=300, blank=True)
    curator_statement   = models.TextField()
    curator_name        = models.CharField(max_length=150, default='Curatorial Board')
    start_date          = models.DateField(blank=True, null=True)
    end_date            = models.DateField(blank=True, null=True)
    is_ongoing          = models.BooleanField(default=True)
    featured            = models.BooleanField(default=False)
    cover_image         = models.ImageField(upload_to='exhibitions/', blank=True, null=True)
    paintings           = models.ManyToManyField(Painting, related_name='exhibitions', blank=True)
    commission_rate     = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=7.50,
        help_text="Gallery commission rate percentage for exhibition/auction sales (typically 7-8%, default 7.50%)"
    )
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-featured', '-start_date', '-created_at']

    def __str__(self):
        return self.title


class Inquiry(models.Model):
    INQUIRY_TYPES = [
        ('private_viewing', 'Private Gallery Viewing'),
        ('condition_report', 'Condition & Provenance Report'),
        ('acquisition_inquiry', 'Curatorial Acquisition Inquiry'),
        ('other', 'General Curatorial Question'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'Curator Contacted'),
        ('completed', 'Completed'),
    ]

    painting        = models.ForeignKey(Painting, on_delete=models.CASCADE, related_name='inquiries')
    collector_name  = models.CharField(max_length=200)
    collector_email = models.EmailField()
    collector_phone = models.CharField(max_length=25, blank=True)
    inquiry_type    = models.CharField(max_length=35, choices=INQUIRY_TYPES, default='private_viewing')
    preferred_date  = models.DateField(blank=True, null=True)
    message         = models.TextField(blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return f'{self.get_inquiry_type_display()} — {self.painting.title} ({self.collector_name})'
