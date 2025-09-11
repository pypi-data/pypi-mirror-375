# Custom Migration to inactivate transmitters on sat reentry.

from django.db import migrations

def inactivate_transmitters_on_sat_reentry(apps, schema_editor):
    Transmitter = apps.get_model('base', 'Transmitter')
    Transmitter.objects.filter(
        status='active',
        satellite__satellite_entry__status='re-entered',
    ).update(status='inactive', citation='Satellite decayed'),


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0060_alter_satelliteentry_citation'),
    ]

    operations = [
        migrations.RunPython(inactivate_transmitters_on_sat_reentry),
    ]
