from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0014_rename_subject_guardians_to_legal_representatives'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ('contact__last_name', 'contact__first_name'), 'verbose_name': 'Subject', 'verbose_name_plural': 'Subjects'},
        ),
    ]
