from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceConfigurationViewSet, RawAttendanceLogViewSet, DevicePushView

router = DefaultRouter()
router.register(r'configurations', DeviceConfigurationViewSet)
router.register(r'raw-logs', RawAttendanceLogViewSet)

urlpatterns = [
    path('push/', DevicePushView.as_view(), name='device-push'),
    path('', include(router.urls)),
]
