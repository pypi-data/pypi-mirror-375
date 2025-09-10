from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=128)),
                ('country', django_countries.fields.CountryField(default='DE', max_length=2)),
                ('zip_code', models.CharField(max_length=16)),
                ('street', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=128)),
                ('last_name', models.CharField(max_length=128)),
                ('display_name', models.CharField(max_length=255)),
                ('gender', models.PositiveSmallIntegerField(choices=[(0, 'female'), (1, 'male'), (2, 'diverse')])),
                ('date_of_birth', models.DateField()),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('phone_mobile', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None)),
                ('phone_home', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None)),
                ('phone_work', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None)),
                ('phone_emergency', phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='subjects.address')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='subjects.contact')),
                ('guardians', models.ManyToManyField(blank=True, related_name='subjects', to='subjects.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.PositiveSmallIntegerField(choices=[(0, 'hard of hearing'), (1, 'hard to understand'), (255, 'other')])),
                ('text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='subjects.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Inactivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('until', models.DateField(null=True)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject')),
            ],
        ),
    ]
