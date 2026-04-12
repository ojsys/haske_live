# HASKE Project — Light of Life Website

A Django-based NGO website for **Light of Life / HASKE Project**, a Christian mission organisation reaching unreached people groups across Northern Nigeria.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Project Structure](#3-project-structure)
4. [Getting Started (Local)](#4-getting-started-local)
5. [Environment Variables](#5-environment-variables)
6. [Running the Dev Server](#6-running-the-dev-server)
7. [Database & Migrations](#7-database--migrations)
8. [Admin Panel](#8-admin-panel)
9. [Data Models](#9-data-models)
10. [URL Routes](#10-url-routes)
11. [Frontend Design System](#11-frontend-design-system)
12. [Page Builder (WordPress-like)](#12-page-builder-wordpress-like)
13. [Key APIs](#13-key-apis)
14. [Static & Media Files](#14-static--media-files)
15. [Settings (Local vs Production)](#15-settings-local-vs-production)
16. [Deployment Notes](#16-deployment-notes)
17. [Known Issues & Tech Debt](#17-known-issues--tech-debt)

---

## 1. Project Overview

The site serves as a digital presence for HASKE Project, featuring:

- Public-facing pages: Home, About, Projects, Volunteer, Give, Media/Blog, Contact, Impact Map
- An interactive **Nigeria choropleth map** (Leaflet.js) showing ministry reach by state
- A **horizontal stories carousel** on the home page
- An **admin-managed page builder** that lets non-technical staff create new pages with content blocks (like WordPress)
- A **newsletter subscription** system
- A **volunteer application** form
- A **Django REST Framework** API for demographic/state data

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.1.3 |
| Database (dev) | SQLite |
| Database (prod) | PostgreSQL |
| REST API | Django REST Framework 3.15.2 |
| Frontend CSS | Custom design system (`static/css/haske.css`) |
| Frontend JS | Vanilla JS (no framework) |
| CSS Framework | Bootstrap 5.3.3 (grid/utilities only, visually overridden) |
| Maps | Leaflet.js 1.9.4 + Nigeria GeoJSON |
| Lightbox | PhotoSwipe 5.4.2 |
| Rich Text Editor | CKEditor 4 (django-ckeditor) |
| Admin Theme | Jazzmin 3.0.1 |
| Static Files (prod) | WhiteNoise |
| Config | python-decouple (`.env` file) |
| Fonts | Google Fonts — Playfair Display + Inter |
| Icons | Font Awesome 6.5.1 |

---

## 3. Project Structure

```
haske/
├── manage.py
├── requirements.txt
├── .gitignore
├── .env                        # NOT committed — see §5
│
├── haske_pro/                  # Django project config
│   ├── settings/
│   │   ├── local.py            # Development settings (SQLite, DEBUG=True)
│   │   └── production.py       # Production settings (PostgreSQL, WhiteNoise)
│   ├── urls.py                 # Root URL conf
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                       # The single Django app
│   ├── models.py               # All data models (~730 lines)
│   ├── views.py                # All view functions
│   ├── urls.py                 # App URL patterns
│   ├── admin.py                # Admin registrations + page builder inlines
│   ├── context_processors.py   # Injects logo + nav_custom_pages globally
│   ├── forms.py                # SubscriberForm, VolunteerApplicationForm
│   ├── serializers.py          # DRF serializers for demographic API
│   ├── resources.py            # django-import-export resource classes
│   ├── migrations/             # Database migration files
│   └── templates/
│       ├── base.html           # Site shell: header, footer, nav, scripts
│       └── core/
│           ├── home.html
│           ├── about.html
│           ├── projects.html
│           ├── volunteer.html
│           ├── give.html
│           ├── contact.html
│           ├── media.html
│           ├── blog_list.html
│           ├── blog_detail.html
│           ├── map.html
│           ├── state_detail.html
│           └── demographics_map.html
│       └── pages/              # Page builder templates
│           ├── page.html       # Wrapper that iterates sections
│           └── sections/       # One template per section type
│               ├── hero.html
│               ├── text.html
│               ├── image_text.html
│               ├── cards.html
│               ├── stats.html
│               ├── cta.html
│               ├── gallery.html
│               ├── video.html
│               ├── team.html
│               ├── newsletter.html
│               ├── map.html
│               └── accordion.html
│
├── static/
│   ├── css/
│   │   └── haske.css           # Complete design system (~2 000 lines)
│   └── js/
│       ├── nigeria_map.geojson # Nigeria state boundaries (GeoJSON)
│       └── mapcode.js
│
└── media/                      # Uploaded files (NOT committed to git)
```

---

## 4. Getting Started (Local)

### Prerequisites

- Python 3.12
- pip

### 1. Clone the repo

```bash
git clone <repo-url>
cd haske
```

### 2. Create and activate a virtual environment

```bash
python3.12 -m venv env
source env/bin/activate        # macOS / Linux
env\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

```bash
cp .env.example .env           # if an example exists, otherwise create manually
```

Minimum required content:

```env
SECRET_KEY=your-secret-key-here
```

See [§5 Environment Variables](#5-environment-variables) for the full list.

### 5. Apply migrations

```bash
python manage.py migrate --settings=haske_pro.settings.local
```

### 6. Create a superuser

```bash
python manage.py createsuperuser --settings=haske_pro.settings.local
```

### 7. Load the dev server

```bash
python manage.py runserver --settings=haske_pro.settings.local
```

Visit `http://127.0.0.1:8000/` — the site is live.
Admin panel: `http://127.0.0.1:8000/admin/`

---

## 5. Environment Variables

The project uses **python-decouple**. Create a `.env` file in the project root (`haske/`).

### Local (SQLite)

```env
SECRET_KEY=replace-with-a-long-random-string
```

### Production (PostgreSQL)

```env
SECRET_KEY=replace-with-a-long-random-string
DEBUG=False
DB_NAME=your_db_name
DB_USER_NM=your_db_user
DB_USER_PW=your_db_password
DB_IP=localhost
DB_PORT=5432
```

> **Never commit `.env` to version control.** It is listed in `.gitignore`.

---

## 6. Running the Dev Server

The virtual environment symlinks may break if the project folder is moved. If you see `ModuleNotFoundError: No module named 'django'`, use the explicit PYTHONPATH workaround:

```bash
PYTHONPATH=/path/to/haske/env/lib/python3.12/site-packages \
DJANGO_SETTINGS_MODULE=haske_pro.settings.local \
python3.12 manage.py runserver
```

Or simply recreate the virtual environment in place:

```bash
python3.12 -m venv env --clear
source env/bin/activate
pip install -r requirements.txt
```

---

## 7. Database & Migrations

### Creating migrations after model changes

```bash
python manage.py makemigrations --settings=haske_pro.settings.local
python manage.py migrate --settings=haske_pro.settings.local
```

### Migration history

Key migrations:
- `0001` → initial schema
- `0025_page_pagesection_pagesectioncard` → Page Builder models added

### Resetting the local database

```bash
rm db.sqlite3
python manage.py migrate --settings=haske_pro.settings.local
python manage.py createsuperuser --settings=haske_pro.settings.local
```

---

## 8. Admin Panel

URL: `/admin/`  
Theme: **Jazzmin** (dark sidebar, Bootstrap-based)

### What you can manage

| Section | Model(s) |
|---|---|
| **Site Settings** | SiteLogo |
| **Home Page** | HeroSlide, Statistics, Achievement, MinistrySection, Ministry, Gallery |
| **About Page** | AboutPage, AboutMinistry, MissionVision, Challenge, BoardMember |
| **Projects** | ProjectPage, Project |
| **Volunteer** | VolunteerPage, GoTeam, PrayerPartner, VolunteerApplication |
| **Give / Donate** | DonationPage, BankAccount |
| **Media** | BlogPost, YouTubeVideo, SpotifyPodcast, MediaPage |
| **Contact** | ContactSubmission |
| **Demographics** | DemographicData (importable via Excel/CSV) |
| **Page Builder** | Page → PageSection → PageSectionCard |

### Importing demographic data

`DemographicData` supports bulk import via the **Import** button in admin (Excel or CSV). See `core/resources.py` for the field mapping.

---

## 9. Data Models

All models live in `core/models.py`. They all extend `BaseAuditModel` which adds `created_by`, `last_modified_by`, `created_at`, `updated_at`.

### Core site models

```
SiteLogo            — logo image used in header/footer
HeroSlide           — home page carousel slides (image, title, subtitle, button)
Statistics          — aggregate mission statistics shown on home/map pages
Achievement         — detailed impact numbers (villages, converts, bibles, etc.)
MinistrySection     — "What We Do" intro block
Ministry            — individual ministry pillars (icon, title, description)
Gallery             — photo gallery items (featured flag for home page)
```

### About page models

```
AboutPage           — page title, header image, intro text, ministry goal
AboutMinistry       — ministry items shown on About page
MissionVision       — mission + vision cards with images
Challenge           — 3 challenge cards with images
BoardMember         — board member name, position, bio, photo
```

### Projects / Volunteer / Give

```
ProjectPage         — page header + intro
Project             — individual project (title, description, image, location, beneficiaries)
VolunteerPage       — page header + intro
GoTeam              — Go-Team card (image, title, description)
PrayerPartner       — Prayer Partner card (image, title, description)
VolunteerApplication — submitted applications from the volunteer form
GiveSection         — currently unused legacy model
DonationPage        — give page header + description
BankAccount         — bank transfer details (bank name, account number, account name)
```

### Media

```
BlogPost            — title, slug, featured_image, content (CKEditor), excerpt, author
YouTubeVideo        — title, embed_url, description
SpotifyPodcast      — title, duration
MediaPage           — section titles for the media center page
```

### Demographics / Map

```
DemographicData     — state, LGA, ward, village-level data including population,
                      converts, film attendees, etc. Supports bulk import.
```

### Page Builder

```
Page                — title, slug, meta description, header image, nav settings
PageSection         — belongs to Page; type (hero/text/image_text/cards/stats/cta/
                      gallery/video/team/newsletter/map/accordion), order, content fields,
                      background colour, extra_data JSON
PageSectionCard     — belongs to PageSection; icon, image, title, body, link
```

---

## 10. URL Routes

| URL | View | Name |
|---|---|---|
| `/` | `home` | `home` |
| `/about/` | `about` | `about` |
| `/projects/` | `projects` | `projects` |
| `/volunteer/` | `volunteer` | `volunteer` |
| `/volunteer/apply/` | `volunteer_apply` | `volunteer-apply` |
| `/give/` | `give` | `give` |
| `/media/` | `media_center` | `media` |
| `/blog/` | `blog_list` | `blog-list` |
| `/blog/<slug>/` | `blog_detail` | `blog-detail` |
| `/contact/` | `contact` | `contact` |
| `/map/` | `map_view` | `map` |
| `/state/<name>/` | `state_detail` | `state_detail` |
| `/subscribe/` | `subscribe` | `subscribe` |
| `/pages/<slug>/` | `custom_page` | `custom_page` |
| `/api/states-with-data/` | `states_with_data` | `states_with_data` |
| `/api/state-data/` | `get_state_data` | `state-data` |
| `/api/state-data/<name>/` | `get_state_detail` | `state-detail` |
| `/api/demographics/<state>/` | `StateDemographicView` | `state-demographics` |
| `/demographics-map/` | `DemographicsMapView` | `demographics-map` |
| `/admin/` | Django admin | — |
| `/admin/audit-log/` | `AuditLogView` | `audit_log` |

---

## 11. Frontend Design System

All styles are in **`static/css/haske.css`** (~2 000 lines). There is no build step — it is plain CSS with custom properties.

### Colour palette

```css
--navy:       #0B1F3A   /* primary dark blue */
--gold:       #C8922A   /* accent gold */
--green:      #1D6A4A   /* secondary green */
--amber:      #E8821A   /* warm accent */
--cream:      #FAF8F3   /* off-white background */
```

### Typography

- **Headings** — `Playfair Display` (serif), loaded from Google Fonts
- **Body** — `Inter` (sans-serif), loaded from Google Fonts

### Key CSS patterns

| Class / selector | Purpose |
|---|---|
| `[data-animate]` | Fade-up on scroll (IntersectionObserver in base.html) |
| `[data-counter]` | Counts up to target number on scroll |
| `.section` | Standard section padding (5rem 0) |
| `.section-eyebrow` | Small gold uppercase label above headings |
| `.divider` | Gold underline accent below headings |
| `.page-banner.about-banner` | Full-screen page hero banner |
| `.home-statement-section` | Navy italic pull-quote band |
| `.hscroll-*` | Horizontal scroll carousel |
| `.about-mv-*` | Mission/Vision split cards |
| `.about-challenge-*` | Asymmetric challenge card layout |
| `.about-member-card` | Board member portrait card + modal |
| `.home-impact-*` | Dark cinematic impact number cards |
| `.home-involve-*` | Get Involved section with masonry gallery |
| `.home-verse-*` | Scripture break section |
| `.give-bank-card` | Bank account display with copy button |
| `.contact-info-panel` | Navy contact info box |
| `.imap-*` | Impact map page layout |
| `.vol-path-card` | Volunteer path cards |

### JavaScript (in base.html)

All global JS is inline at the bottom of `base.html`:

- **Scroll handler** — swaps `.is-transparent` ↔ `.is-scrolled` on the header
- **Mobile nav** — hamburger open/close with overlay
- **Dropdown** — click-to-toggle on mobile (`≤991px`), CSS hover on desktop
- **IntersectionObserver** — triggers `is-visible` class on `[data-animate]` elements
- **Counter animation** — `[data-counter]` elements count up when scrolled into view
- **Scroll-to-top button**

Page-specific JS lives in `{% block js %}` in each template.

---

## 12. Page Builder (WordPress-like)

The page builder lets admin staff create fully custom pages without touching code.

### How it works

1. Go to **Admin → Page Builder → Pages → Add Page**
2. Set a title (the slug auto-generates), upload a header image, set SEO description
3. Toggle **Show in nav** to add it to the navigation bar automatically
4. Add **Sections** inline — each section has a type, order, and content fields
5. Some section types (Cards, Team) support **Cards** as a nested inline

### Section types

| Type | Description |
|---|---|
| `hero` | Full-width banner with title, subtitle, and CTA buttons |
| `text` | Rich text content block |
| `image_text` | Image on one side, text on the other (position configurable) |
| `cards` | Grid of icon/image cards (uses PageSectionCard) |
| `stats` | Impact statistics with counters |
| `cta` | Call-to-action banner with buttons |
| `gallery` | Photo grid with PhotoSwipe lightbox |
| `video` | YouTube/Vimeo embed |
| `team` | Team member portraits (uses PageSectionCard) |
| `newsletter` | Email subscription form |
| `map` | Interactive Nigeria map |
| `accordion` | FAQ / expandable items (stored as JSON in `extra_data`) |

### Accordion / custom stats JSON format

The `extra_data` field on `PageSection` accepts JSON for accordion items:

```json
[
  {"question": "What is HASKE?", "answer": "Light of Life mission..."},
  {"question": "How do I give?", "answer": "Via bank transfer or online..."}
]
```

### Template rendering

`pages/page.html` iterates sections and includes the matching template dynamically:

```django
{% include "pages/sections/"|add:section.section_type|add:".html" %}
```

---

## 13. Key APIs

All JSON endpoints are in `core/views.py`.

### `GET /api/states-with-data/`

Returns aggregated data per state for the Leaflet map.

```json
{
  "Kano": {
    "total_population": 15000000,
    "village_count": 42,
    "total_converts": 1200
  }
}
```

### `GET /api/state-data/<state_name>/`

Returns LGA-level detail for a given state.

### `POST /subscribe/`

Newsletter subscription. Accepts `email` via `FormData`. Returns:

```json
{ "status": "success", "message": "Thank you for subscribing!" }
```

### `POST /volunteer/apply/`

Volunteer application form. Accepts `full_name`, `email`, `phone`, `area_of_interest`, `skills`, `availability`, `message`. Returns status JSON.

---

## 14. Static & Media Files

### Static files

Source static files live in `static/` at the project root.

`STATICFILES_DIRS = [BASE_DIR.parent / 'static']` (points to `haske/static/`)

In production, run:

```bash
python manage.py collectstatic --settings=haske_pro.settings.production
```

This copies everything into `staticfiles/`, which WhiteNoise serves.

### Media files

User-uploaded files (images, documents) are stored in `media/` and are **not committed to Git**.

On a new server, create the directory and ensure the web server / WhiteNoise can serve from `MEDIA_ROOT`.

---

## 15. Settings (Local vs Production)

| Setting | Local (`local.py`) | Production (`production.py`) |
|---|---|---|
| `DEBUG` | `True` | `False` (from env) |
| `DATABASE` | SQLite (`db.sqlite3`) | PostgreSQL (from env vars) |
| `SECRET_KEY` | from `.env` | from `.env` |
| `SECURE_SSL_REDIRECT` | `False` | `True` (enable when SSL is configured) |
| `SESSION_COOKIE_SECURE` | `False` | `True` |
| `CSRF_COOKIE_SECURE` | `False` | `True` |
| Static serving | Django dev server | WhiteNoise middleware |
| Context processor | `site_globals` included | **Missing** — add to production |

> **Important:** `core.context_processors.site_globals` is present in `local.py` but **missing from `production.py`**. Add it to the `TEMPLATES` context processors list before deploying, or the logo and custom nav pages will not appear.

---

## 16. Deployment Notes

### WSGI

The project ships a `passenger_wsgi.py` for shared hosting (cPanel / Passenger), and the standard `haske_pro/wsgi.py` for gunicorn.

**Gunicorn:**

```bash
gunicorn haske_pro.wsgi:application \
  --workers 3 \
  --bind 0.0.0.0:8000 \
  --env DJANGO_SETTINGS_MODULE=haske_pro.settings.production
```

### Checklist before going live

- [ ] Set `DEBUG=False` in production `.env`
- [ ] Set a strong `SECRET_KEY`
- [ ] Set correct `ALLOWED_HOSTS`
- [ ] Add `site_globals` context processor to `production.py`
- [ ] Configure PostgreSQL credentials in `.env`
- [ ] Run `collectstatic`
- [ ] Configure `MEDIA_ROOT` to a persistent storage location
- [ ] Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] Configure a reverse proxy (nginx / Apache) in front of gunicorn
- [ ] Set up periodic backups of the database and `media/` directory

---

## 17. Known Issues & Tech Debt

| Issue | Detail |
|---|---|
| **CKEditor 4 security warning** | django-ckeditor bundles CKEditor 4 which has known XSS issues. Consider migrating to `django-ckeditor-5` or another editor. |
| **`/Report_test/` route** | Maps to the `about` view — a leftover dev route. Can be safely removed from `core/urls.py`. |
| **`production.py` missing context processor** | `core.context_processors.site_globals` is absent from the production settings template list. The logo and custom nav pages will not render until this is added. |
| **`CORS_ALLOW_ALL_ORIGINS = True`** | Both settings files allow all origins. Restrict this to known domains before going live. |
| **`ALLOWED_HOSTS = ['*']`** | Both settings files allow all hosts. Set explicitly in production. |
| **No email backend configured** | Contact form and volunteer applications save to the database but do not send email notifications. Add `EMAIL_BACKEND` and notification logic as needed. |
| **Broken venv symlinks** | If the project folder is moved, venv Python symlinks break. Recreate with `python3.12 -m venv env --clear`. |
