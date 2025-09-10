from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0005_auto_20221011_0432'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Contact',
            new_name='ContactOld',
        ),
    ]
