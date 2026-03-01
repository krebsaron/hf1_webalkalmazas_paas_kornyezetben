# PhotoAlbum – Cloud-based Photo Album Application

A Django-based photo album web application deployed on Heroku.

## Features

- **Photo upload / delete** – with image preview before upload
- **Photo metadata** – name (max 40 characters) and upload timestamp (YYYY-MM-DD HH:MM)
- **Gallery listing** – sortable by name (A→Z, Z→A) or date (newest/oldest first)
- **Search** – filter photos by name
- **Photo detail view** – full-size image with metadata on click
- **User management** – registration, login, logout
- **Access control** – upload and delete restricted to authenticated users; only the owner (or admin staff) can delete their photos
- **Responsive UI** – Bootstrap 5, works on mobile and desktop

## Architecture (Multi-tier, Scalable)

```
[Browser]
   ↓ HTTPS
[Heroku Dyno – Gunicorn + Django]   ← web tier (horizontally scalable)
   ↓                  ↓
[Heroku PostgreSQL]   [Cloudinary CDN]
  (data tier)         (media/image storage)
```

| Layer | Technology | Role |
|-------|-----------|------|
| Web/App | Django + Gunicorn on Heroku | Request handling, business logic |
| Static files | WhiteNoise | Serves CSS/JS directly from the dyno |
| Database | Heroku Postgres (add-on) | Relational data: users, photo metadata |
| Media storage | Cloudinary | Persistent image file storage (Heroku filesystem is ephemeral) |

## Local Development

### Prerequisites

- Python 3.12+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <project-folder>

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set SECRET_KEY (and optionally DEBUG=True)

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (optional)
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

> **Note:** Locally, photos are stored in the `media/` directory (SQLite database).  
> The `media/` folder is excluded from git to avoid committing binary files.

---

## Deploying to Heroku

### 1. Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account
- [Cloudinary account](https://cloudinary.com/) (free tier is sufficient)

### 2. Create Heroku app

```bash
heroku create your-app-name
```

### 3. Add PostgreSQL add-on

```bash
heroku addons:create heroku-postgresql:essential-0
```

### 4. Set Config Vars

```bash
# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

heroku config:set SECRET_KEY='<generated-key>'
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com'
heroku config:set CSRF_TRUSTED_ORIGINS='https://your-app-name.herokuapp.com'
heroku config:set DB_SSL_REQUIRE=True

# Cloudinary credentials (from your Cloudinary dashboard)
heroku config:set USE_CLOUDINARY=True
heroku config:set CLOUDINARY_CLOUD_NAME='your-cloud-name'
heroku config:set CLOUDINARY_API_KEY='your-api-key'
heroku config:set CLOUDINARY_API_SECRET='your-api-secret'
```

### 5. Connect GitHub for automatic deploys

1. Go to your Heroku app → **Deploy** tab
2. Select **GitHub** as deployment method
3. Connect your repository
4. Enable **Automatic Deploys** from the `main` branch

Every push to `main` will automatically trigger a new build and deployment.

### 6. Initial deploy (manual push or via GitHub)

```bash
git push heroku main
```

The `Procfile` `release` phase runs automatically:
- `python manage.py migrate --no-input`
- `python manage.py collectstatic --no-input --clear`

### 7. Create a superuser on Heroku

```bash
heroku run python manage.py createsuperuser
```

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | `True` for dev, `False` for prod (default: `False`) |
| `ALLOWED_HOSTS` | Yes (prod) | Comma-separated allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | Yes (prod) | Comma-separated trusted origins (include `https://`) |
| `DATABASE_URL` | Auto (Heroku) | PostgreSQL connection string (set by Heroku add-on) |
| `DB_SSL_REQUIRE` | No | `True` for Heroku Postgres (default: `False`) |
| `USE_CLOUDINARY` | No | `True` to use Cloudinary for media storage |
| `CLOUDINARY_CLOUD_NAME` | If Cloudinary | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | If Cloudinary | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | If Cloudinary | Cloudinary API secret |

---

## Project Structure

```
.
├── photoalbum/          # Django project configuration
│   ├── settings.py      # Settings (env-based, works locally and on Heroku)
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI entry point for Gunicorn
├── photos/              # Main application
│   ├── models.py        # Photo model
│   ├── views.py         # All view functions
│   ├── forms.py         # PhotoUploadForm, RegisterForm
│   ├── urls.py          # App URL patterns
│   └── admin.py         # Django admin configuration
├── templates/           # HTML templates
│   ├── base.html        # Base template (navbar, messages, footer)
│   ├── registration/    # Auth templates (login, register)
│   └── photos/          # Photo templates (list, detail, upload, delete)
├── static/css/          # Custom CSS
├── manage.py
├── requirements.txt     # Python dependencies
├── Procfile             # Heroku process definitions
├── runtime.txt          # Python version for Heroku
└── .env.example         # Environment variable template
```
