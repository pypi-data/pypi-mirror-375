import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0011_delete_inactivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='contact',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='subjects.contact', verbose_name='Contact'),
        ),
    ]
