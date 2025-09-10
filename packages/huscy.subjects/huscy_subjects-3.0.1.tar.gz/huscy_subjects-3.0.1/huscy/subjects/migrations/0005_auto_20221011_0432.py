from django.db import migrations, models
import django_countries.fields
import phonenumber_field.modelfields


def forward_function(apps, schema_editor):
    Contact = apps.get_model('subjects', 'Contact')
    contacts = []
    for contact in Contact.objects.all():
        contact.city = contact.address.city
        contact.country = contact.address.country
        contact.postal_code = contact.address.zip_code
        contact.street = contact.address.street
        contacts.append(contact)
    Contact.objects.bulk_update(contacts, ['city', 'country', 'postal_code', 'street'])


class Migration(migrations.Migration):

    dependencies = [
        ('subjects', '0004_delete_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='city',
            field=models.CharField(default='', max_length=128, verbose_name='City'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contact',
            name='country',
            field=django_countries.fields.CountryField(default='DE', max_length=2, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='contact',
            name='postal_code',
            field=models.CharField(default='', max_length=16, verbose_name='Postal code'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contact',
            name='street',
            field=models.CharField(default='', max_length=255, verbose_name='Street'),
            preserve_default=False,
        ),

        migrations.RunPython(forward_function),

        migrations.RemoveField(
            model_name='contact',
            name='address',
        ),
        migrations.DeleteModel(
            name='Address',
        ),
    ]
