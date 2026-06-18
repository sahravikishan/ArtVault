from django.shortcuts import render, get_object_or_404
from .models import Artist


def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    paintings = artist.painting_set.all()
    return render(request, 'artists/artist_detail.html', {
        'artist': artist,
        'paintings': paintings,
    })
