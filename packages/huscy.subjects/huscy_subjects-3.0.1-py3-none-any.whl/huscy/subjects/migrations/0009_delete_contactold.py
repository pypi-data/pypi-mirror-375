from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0008_auto_20221018_0935'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ContactOld',
        ),
    ]
