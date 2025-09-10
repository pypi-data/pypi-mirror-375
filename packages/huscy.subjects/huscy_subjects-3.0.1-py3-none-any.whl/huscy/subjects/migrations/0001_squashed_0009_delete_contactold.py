import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.migrations.operations.special
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    replaces = [('subjects', '0001_initial'), ('subjects', '0002_auto_20210810_0124'), ('subjects', '0003_auto_20211028_1133'), ('subjects', '0004_delete_note'), ('subjects', '0005_auto_20221011_0432'), ('subjects', '0006_rename_contact_contactold'), ('subjects', '0007_contact'), ('subjects', '0008_auto_20221018_0935'), ('subjects', '0009_delete_contactold')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=128, verbose_name='First name')),
                ('last_name', models.CharField(max_length=128, verbose_name='Last name')),
                ('display_name', models.CharField(max_length=255, verbose_name='Display name')),
                ('gender', models.PositiveSmallIntegerField(choices=[(0, 'female'), (1, 'male'), (2, 'diverse')], verbose_name='Gender')),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('city', models.CharField(max_length=128, verbose_name='City')),
                ('country', django_countries.fields.CountryField(default='DE', max_length=2, verbose_name='Country')),
                ('postal_code', models.CharField(max_length=16, verbose_name='Postal code')),
                ('street', models.CharField(max_length=255, verbose_name='Street')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='Email')),
                ('phone_mobile', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone mobile')),
                ('phone_home', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone home')),
                ('phone_work', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone work')),
                ('phone_emergency', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone emergency')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='subjects.contact', verbose_name='Contact')),
                ('guardians', models.ManyToManyField(blank=True, related_name='subjects', to='subjects.Contact', verbose_name='Guardians')),
            ],
            options={
                'ordering': ('contact__last_name', 'contact__first_name'),
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
        ),
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject')),
            ],
            options={
                'ordering': ('subject__contact__last_name', 'subject__contact__first_name'),
                'verbose_name': 'Child',
                'verbose_name_plural': 'Children',
            },
        ),
        migrations.CreateModel(
            name='Inactivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('until', models.DateField(null=True, verbose_name='Until')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject')),
            ],
            options={
                'ordering': ('subject__contact__display_name',),
                'verbose_name': 'Inactivity',
                'verbose_name_plural': 'Inactivities',
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject')),
            ],
            options={
                'ordering': ('subject__contact__last_name', 'subject__contact__first_name'),
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
            },
        ),
    ]
