# Backend\companies\urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, DepartmentViewSet

router = DefaultRouter()
router.register(r"companies", CompanyViewSet)
router.register(r"departments", DepartmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
