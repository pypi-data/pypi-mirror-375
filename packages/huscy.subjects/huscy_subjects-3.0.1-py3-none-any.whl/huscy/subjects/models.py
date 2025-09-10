import uuid
from datetime import date

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Contact(models.Model):
    class GENDER(models.IntegerChoices):
        female = 0, _('female')
        male = 1, _('male')
        diverse = 2, _('diverse')

    id = models.UUIDField(_('ID'), primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(_('First name'), max_length=128)  # without middle names
    last_name = models.CharField(_('Last name'), max_length=128)  # without middle names

    # full name with prefixes (titles) and suffixes
    display_name = models.CharField(_('Display name'), max_length=255)

    gender = models.PositiveSmallIntegerField(_('Gender'), choices=GENDER.choices)

    date_of_birth = models.DateField(_('Date of birth'))

    city = models.CharField(_('City'), max_length=128)
    country = CountryField(_('Country'), default='DE')
    postal_code = models.CharField(_('Postal code'), max_length=16)
    street = models.CharField(_('Street'), max_length=255)  # street name & number + additional info

    email = models.EmailField(_('Email'), blank=True, default='')
    phone_mobile = PhoneNumberField(_('Phone mobile'), blank=True, default='')
    phone_home = PhoneNumberField(_('Phone home'), blank=True, default='')
    phone_work = PhoneNumberField(_('Phone work'), blank=True, default='')
    phone_emergency = PhoneNumberField(_('Phone emergency'), blank=True, default='')

    def __str__(self):
        return f'{self.display_name}'

    @property
    def is_assigned_to_subjects(self):
        return self.subjects.exists()

    @property
    def is_subject(self):
        return Subject.objects.filter(contact=self).exists()

    class Meta:
        ordering = 'last_name', 'first_name'
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')


class Subject(models.Model):
    id = models.UUIDField(_('ID'), primary_key=True, default=uuid.uuid4, editable=False)

    contact = models.OneToOneField(Contact, on_delete=models.PROTECT, related_name='+',
                                   verbose_name=_('Contact'))

    is_child = models.BooleanField(_('Is child'), editable=False, default=False)
    legal_representatives = models.ManyToManyField(Contact, blank=True, related_name='subjects',
                                                   verbose_name=_('Legal representatives'))

    @property
    def age_in_years(self):
        today = date.today()
        date_of_birth = self.contact.date_of_birth
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month,
                                                                              date_of_birth.day))

    def __str__(self):
        return str(self.contact)

    class Meta:
        ordering = 'contact__last_name', 'contact__first_name'
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
