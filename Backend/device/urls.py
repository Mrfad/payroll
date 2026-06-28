# Backend\device\urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeviceConfigurationViewSet, DevicePushView, RawAttendanceLogViewSet

router = DefaultRouter()
router.register(r"configurations", DeviceConfigurationViewSet)
router.register(r"raw-logs", RawAttendanceLogViewSet)

urlpatterns = [
    path("push/", DevicePushView.as_view(), name="device-push"),
    path("", include(router.urls)),
]
