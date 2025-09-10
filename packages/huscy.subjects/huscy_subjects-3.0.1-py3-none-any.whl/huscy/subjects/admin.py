from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html_join
from reversion.admin import VersionAdmin

from huscy.subjects import models


@admin.register(models.Contact)
class ContactAdmin(VersionAdmin, admin.ModelAdmin):
    date_hierarchy = 'date_of_birth'
    list_display = ('display_name', 'last_name', 'first_name', 'gender', 'date_of_birth',
                    'address', 'email')
    list_filter = 'gender', 'city'
    search_fields = ('last_name', 'first_name', 'display_name', 'city', 'postal_code', 'street',
                     'email')

    def address(self, contact):
        return f'{contact.country}-{contact.postal_code} {contact.city}, {contact.street}'


@admin.register(models.Subject)
class SubjectAdmin(VersionAdmin, admin.ModelAdmin):
    fields = 'contact', 'legal_representatives'
    list_display = ('id', '_display_name', '_date_of_birth', 'age_in_years',
                    'is_child', '_legal_representatives')
    readonly_fields = 'contact',
    search_fields = 'contact__display_name',

    def _display_name(self, subject):
        return subject.contact.display_name
    _display_name.admin_order_field = 'contact__display_name'

    def _date_of_birth(self, subject):
        return subject.contact.date_of_birth
    _date_of_birth.admin_order_field = 'contact__date_of_birth'

    def _legal_representatives(self, subject):
        return format_html_join(', ', '<a href="{}">{}</a>', [
            (reverse('admin:subjects_contact_change', args=[contact.id]), contact.display_name)
            for contact in subject.legal_representatives.all()
        ])
