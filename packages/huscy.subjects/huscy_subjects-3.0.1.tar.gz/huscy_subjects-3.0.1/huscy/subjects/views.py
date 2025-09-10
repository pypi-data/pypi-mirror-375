from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets, mixins
from reversion import set_comment
from reversion.views import RevisionMixin

from huscy.subjects import pagination, models, serializers, services
from huscy.subjects.permissions import ChangeSubjectPermission, SubjectPermission


class QuerySetLimitFilter(filters.BaseFilterBackend):
    '''
    For data protection reasons it's recommended to limit the number of returned subjects.
    '''
    DEFAULT = 500

    def filter_queryset(self, request, queryset, view):
        if view.action == 'list':
            LIMIT = services._get_setting('subject_viewset_max_result_count', self.DEFAULT)
            queryset = queryset[:LIMIT]
        return queryset


class SubjectViewSet(RevisionMixin, viewsets.ModelViewSet):
    filter_backends = (
        filters.OrderingFilter,
        filters.SearchFilter,
        QuerySetLimitFilter,
    )
    http_method_names = 'get', 'post', 'put', 'delete', 'head', 'options', 'trace'
    ordering_fields = (
        'contact__date_of_birth',
        'contact__first_name',
        'contact__gender',
        'contact__last_name',
    )
    pagination_class = pagination.SubjectPagination
    permission_classes = (SubjectPermission, )
    queryset = services.get_subjects(include_children=True)
    search_fields = 'contact__display_name', 'contact__date_of_birth'
    serializer_class = serializers.SubjectSerializer

    def perform_create(self, serializer):
        subject = serializer.save()
        set_comment(f'Created subject <ID-{subject.id}>')

    def perform_destroy(self, subject):
        services.delete_subject(subject)
        set_comment(f'Deleted subject <ID-{subject.id}')

    def perform_update(self, serializer):
        subject = serializer.save()
        set_comment(f'Updated subject <ID-{subject.id}>')


class LegalRepresentativeViewSet(RevisionMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                 mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'post', 'put', 'delete', 'head', 'options', 'trace'
    permission_classes = (ChangeSubjectPermission, )
    serializer_class = serializers.LegalRepresentativeSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.subject = get_object_or_404(models.Subject, pk=self.kwargs['subject_pk'])

    def get_queryset(self):
        return self.subject.legal_representatives.all()

    def perform_create(self, serializer):
        legal_representative = serializer.save(subject=self.subject)
        set_comment(f'Created legal_representative <ID-{legal_representative.id}>')

    def perform_destroy(self, legal_representative):
        services.remove_legal_representative(self.subject, legal_representative)
        set_comment(f'Deleted legal_representative <ID-{legal_representative.id}>')

    def perform_update(self, serializer):
        legal_representative = serializer.save()
        set_comment(f'Updated legal_representative <ID-{legal_representative.id}>')
