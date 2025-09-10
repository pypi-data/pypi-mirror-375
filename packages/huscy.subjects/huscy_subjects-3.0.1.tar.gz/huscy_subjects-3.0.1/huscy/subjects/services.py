import logging

from django.conf import settings

from huscy.subjects.models import Contact, Subject

logger = logging.getLogger('huscy.subjects')


def _get_setting(key, default):
    huscy_settings = getattr(settings, 'HUSCY', {})
    subjects_settings = huscy_settings.get('subjects', {})
    return subjects_settings.get(key, default)


AGE_OF_MAJORITY = _get_setting('age_of_majority', 18)


def create_contact(first_name, last_name, gender, date_of_birth,
                   country, city, postal_code, street,
                   display_name='',
                   email='', phone_emergency='', phone_home='', phone_mobile='', phone_work=''):
    contact = Contact.objects.create(
        city=city,
        country=country,
        date_of_birth=date_of_birth,
        display_name=display_name if display_name else f'{first_name} {last_name}',
        email=email,
        first_name=first_name,
        gender=gender,
        last_name=last_name,
        phone_emergency=phone_emergency,
        phone_home=phone_home,
        phone_mobile=phone_mobile,
        phone_work=phone_work,
        postal_code=postal_code,
        street=street,
    )
    return contact


def update_contact(contact, first_name, last_name, gender, date_of_birth,
                   country, city, postal_code, street,
                   display_name='',
                   email='', phone_emergency='', phone_home='', phone_mobile='', phone_work=''):
    contact.country = country
    contact.city = city
    contact.date_of_birth = date_of_birth
    contact.display_name = display_name if display_name else contact.display_name
    contact.email = email
    contact.first_name = first_name
    contact.gender = gender
    contact.last_name = last_name
    contact.phone_emergency = phone_emergency
    contact.phone_home = phone_home
    contact.phone_mobile = phone_mobile
    contact.phone_work = phone_work
    contact.postal_code = postal_code
    contact.street = street
    contact.save()
    return contact


def create_subject(contact):
    subject = Subject.objects.create(contact=contact)

    logger.info('Subject id:%d has been created', subject.id)

    if subject.age_in_years < AGE_OF_MAJORITY:
        subject.is_child = True
        subject.save()

    return subject


def delete_subject(subject):
    for contact in subject.legal_representatives.all():
        remove_legal_representative(subject, contact)
    subject.delete()
    subject.contact.delete()


def get_subjects(include_children=False):
    queryset = Subject.objects

    if include_children is False:
        queryset = queryset.exclude(is_child=True)

    return (queryset.select_related('contact')
                    .prefetch_related('legal_representatives')
                    .order_by('contact__last_name', 'contact__first_name'))


def update_subject(subject):
    if subject.age_in_years < AGE_OF_MAJORITY and subject.is_child is False:
        subject.is_child = True
        subject.save()

    return subject


def add_legal_representative(subject, contact):
    if subject.contact == contact:
        raise ValueError('Cannot add contact as legal_representative because it\'s the '
                         'subject itself!')

    subject.legal_representatives.add(contact)
    return contact


def remove_legal_representative(subject, legal_representative):
    subject.legal_representatives.remove(legal_representative)
    if not (legal_representative.is_assigned_to_subjects or legal_representative.is_subject):
        legal_representative.delete()
