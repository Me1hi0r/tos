from django.db import migrations
from django.contrib.auth.models import User
from django.db.transaction import atomic

HOSTLIST = [
    "localhost:1337",
]


def default_data_create(apps, schema_editor):
    with atomic():
        TrackedHost = apps.get_model('tracker', 'TrackedHost')
        for host in HOSTLIST:
            if not TrackedHost.objects.filter(host=host).first():
                new_host = TrackedHost.objects.create(host=host, active=True)
                new_host.save()

        if not User.objects.filter(first_name='admin').first():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            admin.save()


class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(default_data_create, migrations.RunPython.noop),
    ]
