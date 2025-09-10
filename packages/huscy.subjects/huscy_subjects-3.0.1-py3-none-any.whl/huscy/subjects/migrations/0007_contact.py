from django.db import migrations, models
from django.forms.models import model_to_dict
import django_countries.fields
import phonenumber_field.modelfields
import uuid


def copy_contacts(apps, schema_generator):
    Contact = apps.get_model('subjects', 'Contact')
    Subject = apps.get_model('subjects', 'Subject')

    for subject in Subject.objects.all():
        contact_data = model_to_dict(subject.contact, exclude=['id'])
        contact = Contact.objects.create(**contact_data)

        subject.contact_new = contact

        for guardian in subject.guardians.all():
            contact_data = model_to_dict(guardian, exclude=['id'])
            contact = Contact.objects.create(**contact_data)
            subject.guardians_new.add(contact)

        subject.save()


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0006_rename_contact_contactold'),
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
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ('last_name', 'first_name'),
                'abstract': False,
            },
        ),

        migrations.AddField(
            model_name='subject',
            name='contact_new',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, related_name='+', to='subjects.contact', verbose_name='Contact'),
        ),
        migrations.AddField(
            model_name='subject',
            name='guardians_new',
            field=models.ManyToManyField(blank=True, related_name='subjects', to='subjects.Contact', verbose_name='Guardians'),
        ),

        migrations.RunPython(copy_contacts, migrations.RunPython.noop),

        migrations.AlterField(
            model_name='subject',
            name='contact_new',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='+', to='subjects.contact', verbose_name='Contact'),
        ),
    ]
