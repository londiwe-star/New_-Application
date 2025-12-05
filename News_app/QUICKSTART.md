# Quick Start Guide

## Initial Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env` (or create manually)
   - Set at minimum: `SECRET_KEY`, `DEBUG=True`, database credentials

3. **For quick testing with SQLite (no MariaDB setup needed):**
   - In `news_portal/settings.py`, temporarily change database to:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Set up groups:**
   ```bash
   python manage.py setup_groups
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Create sample data (optional):**
   ```bash
   python manage.py create_sample_data
   ```

8. **Run server:**
   ```bash
   python manage.py runserver
   ```

9. **Access:**
   - Home: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin

## Sample Login Credentials (after create_sample_data)

- **Reader:** reader1 / reader123
- **Editor:** editor1 / editor123
- **Journalist:** journalist1 / journalist123

## Common Commands

```bash
# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

## Next Steps

1. Configure email settings in `.env` for notifications
2. Configure Twitter API credentials for auto-posting
3. Set up MariaDB for production
4. Review `README.md` for detailed documentation


