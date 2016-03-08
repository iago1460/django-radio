from rest_framework import routers
from django.conf.urls import url, include

import views


router = routers.DefaultRouter()
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'schedules', views.ScheduleViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]
