from rest_framework import routers
from django.conf.urls import url, include

import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'schedules', views.ScheduleViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
