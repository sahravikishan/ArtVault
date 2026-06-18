# ArtVault 🖼️

A private, personal art-cataloging website built with Django. Catalog your painting collection with artist profiles, style filters, provenance stories, and estimated values — all through a beautiful warm-toned interface.

---

## Features

- **Artist profiles** — bio, photo, birth year, and a grid of all their works
- **Painting catalogue** — title, artist, year, style, story, materials, dimensions, location, and estimated value
- **Style filter** — filter the collection by Realism, Impressionism, Abstract, Surrealism, or Other
- **Gold-framed images** — every painting displayed with an antique gold frame
- **Django Admin** — add, edit, and delete entries through the built-in admin panel

---

## Setup

### 1. Clone / navigate to the project

```bash
cd ArtVault
```

### 2. Create and activate a virtual environment

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Seed sample data

```bash
python manage.py seed_data
```

This creates 3 artists (Elena Vasquez, Hiroshi Tanaka, Amara Osei) and 6 paintings so the site isn't empty on first run.

### 6. Create a superuser (for Admin access)

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password.

### 7. Start the development server

```bash
python manage.py runserver
```

Visit:
- **Home / Collection** → http://127.0.0.1:8000/
- **Admin panel** → http://127.0.0.1:8000/admin/

---

## Project Structure

```
ArtVault/
├── artvault_project/       # Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── artists/                # Artists app
│   ├── models.py           # Artist model
│   ├── admin.py
│   ├── views.py
│   └── urls.py
├── paintings/              # Paintings app
│   ├── models.py           # Painting model
│   ├── admin.py
│   ├── views.py
│   ├── urls.py
│   └── management/
│       └── commands/
│           └── seed_data.py
├── templates/
│   ├── base.html           # Shared layout & design system
│   ├── paintings/
│   │   ├── home.html       # Collection grid + style filter
│   │   └── painting_detail.html
│   └── artists/
│       └── artist_detail.html
├── media/                  # Uploaded images (auto-created)
├── requirements.txt
├── manage.py
└── README.md
```

---

## Uploading Images

Images are uploaded via Django Admin:

1. Go to `/admin/` → **Artists** or **Paintings**
2. Click an entry → use the **Photo** / **Image** field to upload a file
3. Images are stored under `media/artists/` and `media/paintings/`

---

## Painting Styles

| Style | Description |
|---|---|
| Realism | Faithful, detailed depiction of reality |
| Impressionism | Light, colour, and fleeting moments |
| Abstract | Non-representational form and colour |
| Surrealism | Dream-logic and the unconscious |
| Other | Everything else |

---

## Tech Stack

- **Python** 3.10+
- **Django** 4.2
- **Pillow** (image field support)
- **SQLite** (default, no Postgres needed)
- **Google Fonts** — Playfair Display & Inter
