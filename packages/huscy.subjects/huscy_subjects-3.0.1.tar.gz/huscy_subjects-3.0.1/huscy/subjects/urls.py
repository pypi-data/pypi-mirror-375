from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from huscy.subjects import views


router = DefaultRouter()
router.register('subjects', views.SubjectViewSet, basename='subject')

subject_router = NestedSimpleRouter(router, 'subjects', lookup='subject')
subject_router.register('legalrepresentatives',
                        views.LegalRepresentativeViewSet,
                        basename='legalrepresentative')


urlpatterns = [
    path('api/', include(router.urls + subject_router.urls)),
]
