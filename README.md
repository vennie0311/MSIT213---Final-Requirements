# Regional Scholarship Application Portal

A Django-based scholarship application portal with Cloudinary document uploads, education formsets, and a JWT-protected status API.

## Deployment

This project is designed for Render with PostgreSQL. Configure the following environment variables in Render:

- `DJANGO_SECRET_KEY`
- `DEBUG=false`
- `DATABASE_URL`
- `CLOUDINARY_URL`
- `ALLOWED_HOSTS` (optional, comma-separated)

### Render service setup

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn scholarship_portal.wsgi`

## Features

- Secure Cloudinary uploads for identity and supporting documents
- Student registration with honeypot spam protection
- Student dashboard with per-user application access only
- Coordinator dashboard with regional filters and bulk status updates
- JWT API endpoint for academic institutions to verify applicant status
- PostgreSQL-ready settings with static file support

## Superuser Credentials

For grading access, please use the designated superuser:

- User: `admin`
- Password: `AdminPass123!`

> If deploying to Render, create the superuser with the provided credentials after deployment using `python manage.py createsuperuser --email admin@example.com --username admin`.

## Local setup

1. Create a virtual environment:
   - `python -m venv venv`
2. Activate it:
   - Windows: `venv\Scripts\activate`
3. Install requirements:
   - `pip install -r requirements.txt`
4. Create `.env` with local development values:
   - `DJANGO_SECRET_KEY=replace-this-with-a-secret`
   - `DEBUG=True`
   - `DATABASE_URL=sqlite:///db.sqlite3`
   - `CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name`
5. Run migrations:
   - `python manage.py migrate`
6. Create the admin account:
   - `python manage.py createsuperuser --email admin@example.com --username admin`
7. Start the server:
   - `python manage.py runserver`

## API Documentation

See `postman_collection.json` for a ready-to-import Postman collection with JWT token flows and application status verification requests.

## Security Audit

Audit reports are included in `security_audit_report.md` and `security_audit_report.pdf`. Run the following checks locally:

- `pip-audit`
- `bandit -r portal scholarship_portal`
- `python manage.py check --deploy`
