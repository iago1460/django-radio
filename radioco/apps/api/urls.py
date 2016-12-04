from rest_framework import routers
import views


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'programmes', views.ProgrammeViewSet)
router.register(r'episodes', views.EpisodeViewSet)
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'transmissions', views.TransmissionViewSet, base_name='transmission')
router.register(r'operations', views.TransmissionOperationViewSet, base_name='operation')

urlpatterns = router.urls
