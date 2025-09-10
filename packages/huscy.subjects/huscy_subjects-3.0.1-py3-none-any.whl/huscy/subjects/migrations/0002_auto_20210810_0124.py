from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subjects', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ('country', 'city', 'zip_code', 'street'), 'verbose_name': 'Address', 'verbose_name_plural': 'Addresses'},
        ),
        migrations.AlterModelOptions(
            name='child',
            options={'ordering': ('subject__contact__last_name', 'subject__contact__first_name'), 'verbose_name': 'Child', 'verbose_name_plural': 'Children'},
        ),
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ('last_name', 'first_name'), 'verbose_name': 'Contact', 'verbose_name_plural': 'Contacts'},
        ),
        migrations.AlterModelOptions(
            name='inactivity',
            options={'ordering': ('subject__contact__display_name',), 'verbose_name': 'Inactivity', 'verbose_name_plural': 'Inactivities'},
        ),
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ('subject__contact__display_name', '-created_at'), 'verbose_name': 'Note', 'verbose_name_plural': 'Notes'},
        ),
        migrations.AlterModelOptions(
            name='patient',
            options={'ordering': ('subject__contact__last_name', 'subject__contact__first_name'), 'verbose_name': 'Patient', 'verbose_name_plural': 'Patients'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ('contact__last_name', 'contact__first_name'), 'verbose_name': 'Subject', 'verbose_name_plural': 'Subjects'},
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=128, verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=django_countries.fields.CountryField(default='DE', max_length=2, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=255, verbose_name='Street'),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(max_length=16, verbose_name='Zip code'),
        ),
        migrations.AlterField(
            model_name='child',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='subjects.address', verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='display_name',
            field=models.CharField(max_length=255, verbose_name='Display name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='first_name',
            field=models.CharField(max_length=128, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='gender',
            field=models.PositiveSmallIntegerField(choices=[(0, 'female'), (1, 'male'), (2, 'diverse')], verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='last_name',
            field=models.CharField(max_length=128, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_emergency',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone emergency'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_home',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone home'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_mobile',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone mobile'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='phone_work',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region=None, verbose_name='Phone work'),
        ),
        migrations.AlterField(
            model_name='inactivity',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='inactivity',
            name='until',
            field=models.DateField(null=True, verbose_name='Until'),
        ),
        migrations.AlterField(
            model_name='note',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created at'),
        ),
        migrations.AlterField(
            model_name='note',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Creator'),
        ),
        migrations.AlterField(
            model_name='note',
            name='option',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Hard of hearing'), (1, 'Hard to understand'), (255, 'Other')], verbose_name='Option'),
        ),
        migrations.AlterField(
            model_name='note',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='subjects.subject', verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='note',
            name='text',
            field=models.TextField(blank=True, verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subjects.subject', verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='subjects.contact', verbose_name='Contact'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='guardians',
            field=models.ManyToManyField(blank=True, related_name='subjects', to='subjects.Contact', verbose_name='Guardians'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
