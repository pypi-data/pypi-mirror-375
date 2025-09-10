from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0013_alter_subject_options_subject_is_child_delete_child'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subject',
            old_name='guardians',
            new_name='legal_representatives',
        ),

        migrations.AlterField(
            model_name='subject',
            name='legal_representatives',
            field=models.ManyToManyField(blank=True, related_name='subjects', to='subjects.contact', verbose_name='Legal representatives'),
        ),
    ]
