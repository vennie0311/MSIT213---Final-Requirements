import os
from dotenv import load_dotenv
load_dotenv()
import django
import sys
# ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','scholarship_portal.settings')
django.setup()
from django.core.files import File
from portal.models import ScholarshipApplication

MEDIA_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))

fields = ['identity_document', 'transcript_document', 'proof_of_address']

count_uploaded = 0
for app in ScholarshipApplication.objects.all():
    for field_name in fields:
        f = getattr(app, field_name)
        # skip if empty
        if not f:
            continue
        try:
            # local filesystem path
            local_path = f.path
        except Exception:
            # if storage backend is already remote, skip
            print(f"Skipping {app.id} {field_name}: not a local file path")
            continue
        if not os.path.exists(local_path):
            print(f"File not found for app {app.id} field {field_name}: {local_path}")
            continue
        # reopen and save to trigger upload to default storage (Cloudinary)
        with open(local_path, 'rb') as fh:
            django_file = File(fh)
            # use same basename
            name = os.path.basename(local_path)
            getattr(app, field_name).save(name, django_file, save=False)
            print(f"Queued upload for app {app.id} field {field_name}: {name}")
            count_uploaded += 1
    app.save()

print(f"Done. Files queued and saved: {count_uploaded}")
