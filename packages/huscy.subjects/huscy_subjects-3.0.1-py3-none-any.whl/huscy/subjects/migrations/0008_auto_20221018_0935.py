from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0007_contact'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='guardians',
        ),

        migrations.RenameField(
            model_name='subject',
            old_name='contact_new',
            new_name='contact',
        ),
        migrations.RenameField(
            model_name='subject',
            old_name='guardians_new',
            new_name='guardians',
        ),
    ]
