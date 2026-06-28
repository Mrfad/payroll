# Backend\prj\urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "api/v1/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"
    ),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/companies/", include("companies.urls")),
    path("api/v1/employees/", include("employees.urls")),
    path("api/v1/attendance/", include("attendance.urls")),
    path("api/v1/audit/", include("audit.urls")),
    path("api/v1/payroll/", include("payroll.urls")),
    path("api/v1/device/", include("device.urls")),
    path("api-auth/", include("rest_framework.urls")),
    # Swagger API Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)