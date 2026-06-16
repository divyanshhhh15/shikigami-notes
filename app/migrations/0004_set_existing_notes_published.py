from django.db import migrations


def set_existing_notes_to_published(apps, schema_editor):
    Note = apps.get_model('app', 'Note')
    Note.objects.filter(ispublished=False).update(ispublished=True)


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_note_ispublished'),
    ]

    operations = [
        migrations.RunPython(set_existing_notes_to_published, migrations.RunPython.noop),
    ]
