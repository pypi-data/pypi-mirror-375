from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0010_delete_patient'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Inactivity',
        ),
    ]
