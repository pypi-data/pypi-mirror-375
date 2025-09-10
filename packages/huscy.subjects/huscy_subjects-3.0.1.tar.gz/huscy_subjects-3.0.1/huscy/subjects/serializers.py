from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from huscy.subjects import models, services


class AddressSerializer(serializers.ModelSerializer):
    country = CountryField(initial='DE')

    class Meta:
        model = models.Contact
        fields = (
            'city',
            'country',
            'postal_code',
            'street',
        )


class ContactSerializer(serializers.ModelSerializer):
    address = AddressSerializer(write_only=True)
    display_name = serializers.CharField(allow_blank=True, default='')
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    phone_emergency = PhoneNumberField(allow_blank=True, default='')
    phone_home = PhoneNumberField(allow_blank=True, default='')
    phone_mobile = PhoneNumberField(allow_blank=True, default='')
    phone_work = PhoneNumberField(allow_blank=True, default='')

    class Meta:
        model = models.Contact
        fields = (
            'address',
            'date_of_birth',
            'display_name',
            'email',
            'first_name',
            'gender',
            'gender_display',
            'last_name',
            'phone_emergency',
            'phone_home',
            'phone_mobile',
            'phone_work',
        )

    def to_representation(self, contact):
        data = super().to_representation(contact)
        data['address'] = AddressSerializer(contact).data
        return data

    def create(self, validated_data):
        address_serializer = AddressSerializer(data=validated_data.pop('address'))
        address_serializer.is_valid(raise_exception=True)
        return services.create_contact(**validated_data, **address_serializer.data)

    def update(self, contact, validated_data):
        address_serializer = AddressSerializer(data=validated_data.pop('address'))
        address_serializer.is_valid(raise_exception=True)
        return services.update_contact(contact, **validated_data, **address_serializer.data)


class LegalRepresentativeSerializer(ContactSerializer):
    class Meta:
        model = models.Contact
        fields = ('id', ) + ContactSerializer.Meta.fields

    def create(self, validated_data):
        subject = validated_data.pop('subject')
        contact = super().create(validated_data)
        return services.add_legal_representative(subject, contact)


class SubjectSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    legal_representatives = LegalRepresentativeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Subject
        fields = (
            'id',
            'age_in_years',
            'contact',
            'is_child',
            'legal_representatives',
        )

    def create(self, validated_data):
        contact_serializer = ContactSerializer(data=validated_data.pop('contact'))
        contact_serializer.is_valid(raise_exception=True)
        contact = contact_serializer.save()

        return services.create_subject(contact, **validated_data)

    def update(self, subject, validated_data):
        contact_serializer = ContactSerializer(subject.contact, data=validated_data.pop('contact'))
        contact_serializer.is_valid(raise_exception=True)
        contact_serializer.save()

        return services.update_subject(subject, **validated_data)
