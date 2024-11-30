from rest_framework import routers
from radioco.apps.api import views
from django.urls import include, re_path


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'episodes', views.EpisodeViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'transmissions', views.TransmissionViewSet, basename='transmission')
router.register(r'operations', views.TransmissionOperationViewSet, basename='operation')

radiocom_router = routers.DefaultRouter(trailing_slash=False)
radiocom_router.register(r'programmes', views.RadiocomProgrammeViewSet, basename='radiocom_programmes')
radiocom_router.register(r'transmissions', views.RadiocomTransmissionViewSet, basename='radiocom_transmission')
radiocom_router.register(r'radiostation', views.RadiocomStation, basename='radiocom_radiostation')

urlpatterns = router.urls + [
    re_path(r'^radiocom/', include(radiocom_router.urls)),
]
