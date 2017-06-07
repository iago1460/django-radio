from rest_framework import routers
from radioco.apps.api import views
from django.conf.urls import include, url


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'episodes', views.EpisodeViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'transmissions', views.TransmissionViewSet, base_name='transmission')
router.register(r'operations', views.TransmissionOperationViewSet, base_name='operation')

radiocom_router = routers.DefaultRouter(trailing_slash=False)
radiocom_router.register(r'programmes', views.RadiocomProgrammeViewSet)
radiocom_router.register(r'transmissions', views.RadiocomTransmissionViewSet, base_name='transmission')
radiocom_router.register(r'radiostation', views.RadiocomStation, base_name='radiostation')

urlpatterns = router.urls + [
    url(r'^radiocom/', include(radiocom_router.urls)),
]
