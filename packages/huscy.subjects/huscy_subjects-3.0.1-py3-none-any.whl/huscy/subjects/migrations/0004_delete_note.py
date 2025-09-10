from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0003_auto_20211028_1133'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Note',
        ),
    ]
