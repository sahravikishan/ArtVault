"""
Management command to seed the database with sample artists and paintings.
Run with: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from artists.models import Artist
from paintings.models import Painting


ARTISTS = [
    {
        'name': 'Elena Vasquez',
        'bio': (
            'Elena Vasquez (born 1972, Buenos Aires) is a celebrated Argentine painter known for '
            'her luminous Impressionist landscapes and intimate portraits. After studying at the '
            'Escuela Nacional de Bellas Artes, she spent two decades in Paris absorbing the light '
            'of the Seine and the warmth of Montmartre. Her work captures fleeting moments with '
            'a masterful brush that transforms ordinary scenes into transcendent experiences.'
        ),
        'birth_year': 1972,
    },
    {
        'name': 'Hiroshi Tanaka',
        'bio': (
            'Hiroshi Tanaka (born 1955, Kyoto) is a Japanese abstract painter whose practice '
            'bridges traditional ink-wash techniques with bold contemporary abstraction. Trained '
            'at the Tokyo University of the Arts, Tanaka\'s canvases pulse with meditative energy, '
            'layers of translucent pigment building into labyrinthine compositions that invite '
            'prolonged contemplation. He has exhibited in Tokyo, Berlin, and New York.'
        ),
        'birth_year': 1955,
    },
    {
        'name': 'Amara Osei',
        'bio': (
            'Amara Osei (born 1988, Accra) is a Ghanaian Surrealist painter whose vivid canvases '
            'blend West African mythology with dreamlike European Surrealism. Her work explores '
            'themes of identity, diaspora, and the uncanny, weaving ancestral spirits into '
            'contemporary urban dreamscapes. A graduate of the Kwame Nkrumah University of '
            'Science and Technology, she now works between Accra and London.'
        ),
        'birth_year': 1988,
    },
]

PAINTINGS = [
    {
        'artist_name': 'Elena Vasquez',
        'title': 'Golden Hour Over the Seine',
        'year_created': 2018,
        'style': 'Impressionism',
        'story': (
            'Painted during a summer residency on the banks of the River Seine, this canvas '
            'captures the ephemeral magic of the Parisian golden hour. Vasquez spent three '
            'weeks returning to the same spot each evening, studying how the dying light '
            'dissolved the boundary between water and sky. The thick impasto strokes in the '
            'foreground give way to gossamer glazes in the distance, evoking the sensation '
            'of standing at the water\'s edge as the city holds its breath.'
        ),
        'materials': 'Oil on linen',
        'dimensions': '90 × 120 cm',
        'current_location': 'Private Collection, Paris',
        'estimated_value': '28500.00',
    },
    {
        'artist_name': 'Elena Vasquez',
        'title': 'Portrait of My Mother at Dusk',
        'year_created': 2015,
        'style': 'Realism',
        'story': (
            'A tender homage to Vasquez\'s mother, painted from memory and a single faded '
            'photograph taken in their Buenos Aires home in 1983. The warm amber light filtering '
            'through the shuttered window is rendered with forensic precision, yet the figure '
            'retains a dreamlike softness that speaks to the fallibility of recollection. '
            'This is arguably the artist\'s most personal and emotionally raw work.'
        ),
        'materials': 'Oil on canvas',
        'dimensions': '60 × 75 cm',
        'current_location': 'Artist\'s Studio, Paris',
        'estimated_value': '14200.00',
    },
    {
        'artist_name': 'Hiroshi Tanaka',
        'title': 'Void #7 (The Stillness Between)',
        'year_created': 2021,
        'style': 'Abstract',
        'story': (
            'Part of Tanaka\'s landmark "Void" series, this monumental work explores the '
            'Buddhist concept of mu — nothingness as fertile ground. Over twelve months, '
            'Tanaka applied and removed dozens of translucent ink washes, allowing chance '
            'and gravity to guide rivulets of pigment across the surface. The result is a '
            'composition of hypnotic depth, where near-black voids open into luminous '
            'veins of indigo and silver. To stand before it is to feel the weight of silence.'
        ),
        'materials': 'Sumi ink and mineral pigments on Japanese washi paper, mounted on board',
        'dimensions': '180 × 240 cm',
        'current_location': 'Tanaka Studio, Kyoto',
        'estimated_value': '67000.00',
    },
    {
        'artist_name': 'Hiroshi Tanaka',
        'title': 'Frequencies of Red',
        'year_created': 2019,
        'style': 'Abstract',
        'story': (
            'An explosive departure from Tanaka\'s characteristically restrained palette, '
            '"Frequencies of Red" erupted from a period of personal crisis following the '
            'loss of his mentor and teacher. Seventeen shades of red — from the palest '
            'blush to the deepest crimson — collide and coalesce in a composition that '
            'feels simultaneously violent and tender. Tanaka has described it as "a scream '
            'that learned to sing."'
        ),
        'materials': 'Acrylic and oil stick on canvas',
        'dimensions': '150 × 200 cm',
        'current_location': 'Mori Art Museum, Tokyo (on loan)',
        'estimated_value': '52000.00',
    },
    {
        'artist_name': 'Amara Osei',
        'title': 'The Ancestor Wears a Business Suit',
        'year_created': 2022,
        'style': 'Surrealism',
        'story': (
            'Osei\'s most celebrated work to date, this painting depicts a towering ancestral '
            'spirit — half Adinkra symbol, half city banker — navigating a London commuter '
            'train populated by ghostly passengers. The central figure\'s face is composed '
            'of interlocking kente patterns that shift and reform depending on viewing angle. '
            'The work interrogates what it means to carry heritage into corporate modernity, '
            'and whether assimilation is ever truly complete.'
        ),
        'materials': 'Oil and 24k gold leaf on canvas',
        'dimensions': '120 × 160 cm',
        'current_location': 'Saatchi Gallery, London',
        'estimated_value': '89000.00',
    },
    {
        'artist_name': 'Amara Osei',
        'title': 'Night Market, Accra (Dream Version)',
        'year_created': 2020,
        'style': 'Surrealism',
        'story': (
            'Osei recalls dreaming of the Makola Market in Accra while living in a grey '
            'London flat during the winter of 2019. In the dream, the market stalls sold '
            'memories and the vendors spoke in colours. This painting is her attempt to '
            'render that vision faithfully — the familiar market made radically strange, '
            'its wares replaced by luminous objects that defy categorisation. Bats with '
            'golden wings roost in the rafters; a child holds a jar of bottled moonlight.'
        ),
        'materials': 'Acrylic, oil pastel, and collage on panel',
        'dimensions': '100 × 130 cm',
        'current_location': 'Private Collection, Accra',
        'estimated_value': '41500.00',
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with sample artists and paintings.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding artists...')

        artist_map = {}
        for data in ARTISTS:
            artist, created = Artist.objects.get_or_create(
                name=data['name'],
                defaults={
                    'bio': data['bio'],
                    'birth_year': data['birth_year'],
                }
            )
            artist_map[data['name']] = artist
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {artist.name}')

        self.stdout.write('Seeding paintings...')
        for data in PAINTINGS:
            artist = artist_map[data['artist_name']]
            painting, created = Painting.objects.get_or_create(
                title=data['title'],
                artist=artist,
                defaults={
                    'year_created': data['year_created'],
                    'style': data['style'],
                    'story': data['story'],
                    'materials': data['materials'],
                    'dimensions': data['dimensions'],
                    'current_location': data.get('current_location', ''),
                    'estimated_value': data.get('estimated_value'),
                }
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  {status}: {painting.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {len(ARTISTS)} artists and {len(PAINTINGS)} paintings seeded.'
        ))
