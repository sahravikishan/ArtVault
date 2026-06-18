from django.shortcuts import render, get_object_or_404
from .models import Painting


def home(request):
    style_filter = request.GET.get('style', '')
    paintings = Painting.objects.select_related('artist').all()

    if style_filter:
        paintings = paintings.filter(style=style_filter)

    style_choices = Painting.STYLE_CHOICES

    return render(request, 'paintings/home.html', {
        'paintings': paintings,
        'style_choices': style_choices,
        'active_style': style_filter,
    })


def painting_detail(request, pk):
    painting = get_object_or_404(Painting.objects.select_related('artist'), pk=pk)
    return render(request, 'paintings/painting_detail.html', {
        'painting': painting,
    })
