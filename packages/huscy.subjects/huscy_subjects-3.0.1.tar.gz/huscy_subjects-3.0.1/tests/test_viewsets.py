import pytest
from model_bakery import baker
from pytest_bdd import given, parsers, scenarios, then, when

from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from huscy.subjects.serializers import ContactSerializer

pytestmark = pytest.mark.django_db


scenarios(
    'viewsets/add_legal_representatives.feature',
    'viewsets/create_subjects.feature',
    'viewsets/delete_subjects.feature',
    'viewsets/remove_legal_representatives.feature',
    'viewsets/view_subjects.feature',
    'viewsets/update_subjects.feature',
    'viewsets/update_legal_representatives.feature',
)


@given(parsers.parse('I am {huscy_user}'), target_fixture='client')
def client(admin_user, user, huscy_user):
    assert huscy_user in ['admin user', 'normal user', 'anonymous user']
    api_client = APIClient()
    if huscy_user == 'admin user':
        api_client.login(username=admin_user.username, password='password')
    elif huscy_user == 'normal user':
        api_client.login(username=user.username, password='password')
    elif huscy_user == 'anonymous user':
        pass
    return api_client


@given(parsers.parse('I have {codename} permission'), target_fixture='codename')
def assign_permission(user, codename):
    permission = Permission.objects.get(codename=codename)
    user.user_permissions.add(permission)


@when('I try to add a legal representative', target_fixture='request_result')
def add_legal_representative(client, subject, legal_representative):
    contact = baker.prepare('subjects.Contact')

    return client.post(
        reverse('legalrepresentative-list', kwargs=dict(subject_pk=subject.pk)),
        data=ContactSerializer(contact).data,
        format='json',
    )


@when('I try to create a subject', target_fixture='request_result')
def create_subject(client):
    data = dict(
        contact=dict(
            date_of_birth='2022-10-11',
            first_name='first_name',
            gender=1,
            last_name='last_name',
            address=dict(
                city='Berlin',
                country='DE',
                postal_code='12345',
                street='Hauptstraße 15',
            )
        ),
    )
    return client.post(reverse('subject-list'), data=data, format='json')


@when('I try to delete a subject', target_fixture='request_result')
def delete_subject(client, subject):
    return client.delete(reverse('subject-detail', kwargs=dict(pk=subject.pk)))


@when('I try to list subjects', target_fixture='request_result')
def list_subjects(client):
    return client.get(reverse('subject-list'))


@when('I try to partial update a legal representative', target_fixture='request_result')
def partial_update_legal_representative(client, subject, legal_representative):
    return client.patch(
        reverse('legalrepresentative-detail', kwargs=dict(pk=legal_representative.pk,
                                                          subject_pk=subject.pk)),
        data=dict(),
    )


@when('I try to partial update a subject', target_fixture='request_result')
def partial_update_subject(client, subject):
    return client.patch(
        reverse('subject-detail', kwargs=dict(pk=subject.pk)),
        data=dict(),
    )


@when('I try to remove a legal representative', target_fixture='request_result')
def remove_legal_representative(client, subject, legal_representative):
    return client.delete(
        reverse('legalrepresentative-detail', kwargs=dict(pk=legal_representative.pk,
                                                          subject_pk=subject.pk))
    )


@when('I try to retrieve a subject', target_fixture='request_result')
def retrieve_subject(client, subject):
    return client.get(reverse('subject-detail', kwargs=dict(pk=subject.pk)))


@when('I try to update a legal representative', target_fixture='request_result')
def update_legal_representative(client, subject, legal_representative):
    return client.put(
        reverse('legalrepresentative-detail', kwargs=dict(pk=legal_representative.pk,
                                                          subject_pk=subject.pk)),
        data=ContactSerializer(legal_representative).data,
        format='json',
    )


@when('I try to update a subject', target_fixture='request_result')
def update_subject(client, subject):
    return client.put(
        reverse('subject-detail', kwargs=dict(pk=subject.pk)),
        data=dict(
            contact=ContactSerializer(subject.contact).data,
        ),
        format='json'
    )


@then(parsers.parse('I get status code {status_code:d}'))
def assert_status_code(request_result, status_code):
    assert request_result.status_code == status_code, request_result.content
