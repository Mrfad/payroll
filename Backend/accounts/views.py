# Backend\accounts\views.py
from attendance.models import *
from attendance.serializers import *
from audit.models import *
from audit.serializers import *
from common.models import *
from companies.models import *
from companies.serializers import *
from django.db import transaction
from django.utils import timezone
from employees.models import *
from employees.serializers import *
from payroll.models import *
from payroll.permissions import IsManagerOrDeveloper, IsOwnerOrAdmin
from payroll.serializers import *
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    DjangoModelPermissions,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import *
from accounts.serializers import *


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=["get", "patch"], permission_classes=[])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = request.user.profile
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            data = serializer.data
            data["permissions"] = list(request.user.get_all_permissions())
            data["groups"] = list(request.user.groups.values_list("name", flat=True))
            data["user_id"] = request.user.id
            data["username"] = request.user.username
            if hasattr(request.user, "employee"):
                data["employee_id"] = request.user.employee.id
            return Response(data)
        elif request.method == "PATCH":
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Broadcast the theme update to all connected websocket clients
                if "theme" in request.data:
                    from asgiref.sync import async_to_sync
                    from channels.layers import get_channel_layer

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        "payroll_updates",
                        {
                            "type": "data_update",
                            "model": "userprofile",
                            "action": "theme_updated",
                            "theme": serializer.data["theme"],
                            "user_id": request.user.id,
                        },
                    )

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
