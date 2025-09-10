from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0012_alter_subject_contact'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ('contact__last_name', 'contact__first_name'), 'permissions': (('add_child', 'can add children'), ('delete_child', 'can delete children'), ('change_child', 'can change children'), ('view_child', 'can view children')), 'verbose_name': 'Subject', 'verbose_name_plural': 'Subjects'},
        ),
        migrations.AddField(
            model_name='subject',
            name='is_child',
            field=models.BooleanField(default=False, editable=False, verbose_name='Is child'),
        ),
        migrations.DeleteModel(
            name='Child',
        ),
    ]
