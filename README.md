# FAST CARS Car Rental

Semester 4 project: a Django car-rental site for browsing vehicles, submitting booking requests, contacting the team, and managing the fleet through Django admin.

## Requirements

- Python compatible with Django 6.1.2 (tested with Python 3.14.5)
- pip

## Setup

Run these commands from the folder containing `manage.py`.

### Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py seed_vehicles
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

### macOS or Linux

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py seed_vehicles
venv/bin/python manage.py createsuperuser
venv/bin/python manage.py runserver
```

Open the site at <http://127.0.0.1:8000/>. The admin is at <http://127.0.0.1:8000/django-admin/>. The `createsuperuser` command prompts you to set the admin username and password.

## Sample Vehicles

`seed_vehicles` adds 10 sample brands and 30 sample vehicles. It is safe to run more than once: existing records are not duplicated or overwritten. Seeded car photos are stored in `media/vehicles/` and assigned to their matching sample vehicles. Additional images uploaded through admin are local media files; commit and share them separately if other clones need them.

## Main Features

- Public vehicle listing with search, brand, price, seats, and availability filters, plus pagination and detail pages.
- Featured vehicles on the home page.
- Customer profiles and booking requests with date and availability validation.
- Customer booking history and staff booking management.
- Testimonials with admin moderation.
- Contact messages, subscribers, editable page content, and editable contact details.
- Admin management of brands, vehicles, contact records, subscribers, testimonials, and bookings.

## Tests

Run the full test suite from the project root:

```powershell
python manage.py test
```

Use the active virtual environment's Python executable if `python` does not point to the project environment.

## Database and Backup

The project uses SQLite. The development database is `db.sqlite3` in the project root; Django creates its tables with `manage.py migrate`. The database is excluded from Git, so each clone gets its own database and must run migrations and the seed command.

To make a submission backup, first stop the development server, then copy the database after migrations and sample data have been added:

```powershell
Copy-Item .\db.sqlite3 .\database_backup.sqlite3
```

Keep the backup as a separate submission file rather than committing it to the repository. It may contain account and booking data, so share it only through the intended submission channel.

## Reviewer Credentials

Create an administrator with `manage.py createsuperuser`. SQLite does not require a separate database username or password. Provide the admin username and password to the reviewer through the submission channel; do not put passwords or other secrets in this README or in Git.

## Development Security

The included Django settings are for local development. Before deploying publicly, use a private `SECRET_KEY`, disable `DEBUG`, configure `ALLOWED_HOSTS`, and use an appropriate production database and media-storage setup.
