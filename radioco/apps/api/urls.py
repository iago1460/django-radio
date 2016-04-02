from django.conf.urls import url, include
from rest_framework import routers
import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(
    r'transmissions', views.TransmissionViewSet, base_name='transmission')

urlpatterns = router.urls
