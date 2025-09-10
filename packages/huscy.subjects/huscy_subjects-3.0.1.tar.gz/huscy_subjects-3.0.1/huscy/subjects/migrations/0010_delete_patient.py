from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0001_squashed_0009_delete_contactold'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Patient',
        ),
    ]
