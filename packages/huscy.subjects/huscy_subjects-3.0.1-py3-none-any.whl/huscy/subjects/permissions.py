from rest_framework.permissions import BasePermission, DjangoModelPermissions


class ChangeSubjectPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('subjects.change_subject')


class SubjectPermission(DjangoModelPermissions):
    perms_map = {
        'GET': ['subjects.view_subject'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['subjects.add_subject'],
        'PUT': ['subjects.change_subject'],
        'PATCH': ['subjects.change_subject'],
        'DELETE': ['subjects.delete_subject'],
    }
