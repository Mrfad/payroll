from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.response import Response
from django.db.models import Sum, Count
from datetime import date
from rest_framework.permissions import IsAdminUser, AllowAny, DjangoModelPermissions, IsAuthenticated
from .permissions import IsOwnerOrAdmin, IsManagerOrDeveloper
from .models import (
    Company, Department, Employee, Shift, BreakPolicy, OvertimePolicy,
    ShiftAssignment, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest,
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry, UserProfile, AuditLog
)
from .serializers import (
    CompanySerializer, DepartmentSerializer, EmployeeSerializer, ShiftSerializer,
    BreakPolicySerializer, OvertimePolicySerializer, ShiftAssignmentSerializer,
    AttendanceRecordSerializer, LeaveTypeSerializer, LeaveBalanceSerializer,
    LeaveRequestSerializer, SalaryComponentSerializer, EmployeeSalaryStructureSerializer,
    PayrollPeriodSerializer, PayrollRunSerializer, PayrollEntrySerializer,
    EmployeeEnrollmentSerializer, UserProfileSerializer, AuditLogSerializer
)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [DjangoModelPermissions]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DjangoModelPermissions]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'punch']:
            return [IsAuthenticated()]
        if self.action == 'enroll':
            return [IsManagerOrDeveloper()]
        return [DjangoModelPermissions()]

    def get_queryset(self):
        qs = super().get_queryset()
        show_deleted = self.request.query_params.get('show_deleted')
        if show_deleted == 'true':
            qs = qs.filter(deleted_at__isnull=False)
        else:
            qs = qs.filter(deleted_at__isnull=True)
            
        user = self.request.user
        if user.is_authenticated and not user.is_staff and not user.groups.filter(name__in=['Managers', 'Developers']).exists():
            if hasattr(user, 'employee'):
                qs = qs.filter(id=user.employee.id)
            else:
                qs = qs.none()
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request):
        serializer = EmployeeEnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save()
            return Response({
                'message': 'Employee enrolled successfully',
                'employee_id': employee.employee_id,
                'username': employee.user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        instance = self.get_object()
        old_active = instance.is_active

        diff = []
        for field, new_val in serializer.validated_data.items():
            old_val = getattr(instance, field, None)
            if hasattr(old_val, 'pk'):
                old_val = str(old_val)
            if hasattr(new_val, 'pk'):
                new_val = str(new_val)
            if str(old_val) != str(new_val):
                diff.append(f"{field} changed from '{old_val}' to '{new_val}'")

        employee = serializer.save()
        new_active = employee.is_active
        
        action = 'UPDATE'
        if old_active and not new_active:
            action = 'FREEZE'
        elif not old_active and new_active:
            action = 'UNFREEZE'
            
        details_text = f"Updated employee {employee.employee_id}."
        if diff:
            details_text += " Changes: " + "; ".join(diff)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def punch(self, request, pk=None):
        employee = self.get_object()
        direction = request.data.get('direction', None)
        
        from device.models import DeviceConfiguration, RawAttendanceLog
        from django.utils import timezone
        
        # Get or create a dummy device for app punches
        device, _ = DeviceConfiguration.objects.get_or_create(
            name="App Punch",
            device_type="app",
            company=employee.company,
            defaults={"api_token": "00000000-0000-0000-0000-000000000000"} 
        )
        
        RawAttendanceLog.objects.create(
            device=device,
            external_id=str(employee.employee_id if employee.employee_id else employee.id),
            punch_time=timezone.now(),
            direction=direction,
            raw_data={"source": "app_punch"}
        )
        
        from payroll.services.attendance import AttendanceProcessingService
        AttendanceProcessingService.process_pending_logs()
        
        return Response({"status": "Punch recorded successfully"}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save()
        
        user = instance.user
        user.is_active = False
        user.save()

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.deleted_at = None
        instance.is_active = True
        instance.save()
        
        user = instance.user
        user.is_active = True
        user.save()
        return Response({'status': 'restored'})

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [DjangoModelPermissions]

class BreakPolicyViewSet(viewsets.ModelViewSet):
    queryset = BreakPolicy.objects.all()
    serializer_class = BreakPolicySerializer
    permission_classes = [DjangoModelPermissions]

class OvertimePolicyViewSet(viewsets.ModelViewSet):
    queryset = OvertimePolicy.objects.all()
    serializer_class = OvertimePolicySerializer
    permission_classes = [DjangoModelPermissions]

class ShiftAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ShiftAssignment.objects.all()
    serializer_class = ShiftAssignmentSerializer
    permission_classes = [DjangoModelPermissions]

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]  # Allow all authenticated, we'll restrict in get_queryset

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff and not user.groups.filter(name__in=['Managers', 'Developers']).exists():
            # Regular employee can only see their own attendance
            if hasattr(user, 'employee'):
                qs = qs.filter(employee=user.employee)
            else:
                qs = qs.none()
                
        # Optional filter by employee id
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
            
        return qs.order_by('-date', '-first_in')

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [DjangoModelPermissions]

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsOwnerOrAdmin]

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsOwnerOrAdmin]

class SalaryComponentViewSet(viewsets.ModelViewSet):
    queryset = SalaryComponent.objects.all()
    serializer_class = SalaryComponentSerializer
    permission_classes = [DjangoModelPermissions]

class EmployeeSalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalaryStructure.objects.all()
    serializer_class = EmployeeSalaryStructureSerializer
    permission_classes = [IsOwnerOrAdmin]

class PayrollPeriodViewSet(viewsets.ModelViewSet):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [DjangoModelPermissions]

class PayrollRunViewSet(viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [DjangoModelPermissions]

class PayrollEntryViewSet(viewsets.ModelViewSet):
    queryset = PayrollEntry.objects.all()
    serializer_class = PayrollEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff and not user.groups.filter(name__in=['Managers', 'Developers']).exists():
            if hasattr(user, 'employee'):
                qs = qs.filter(employee=user.employee)
            else:
                qs = qs.none()
                
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
            
        return qs.order_by('-run__period__start_date')

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=['get', 'patch'], permission_classes=[])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        profile = request.user.profile
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            data = serializer.data
            data['permissions'] = list(request.user.get_all_permissions())
            data['groups'] = list(request.user.groups.values_list('name', flat=True))
            data['user_id'] = request.user.id
            data['username'] = request.user.username
            if hasattr(request.user, 'employee'):
                data['employee_id'] = request.user.employee.id
            return Response(data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                # Broadcast the theme update to all connected websocket clients
                if 'theme' in request.data:
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'payroll_updates',
                        {
                            'type': 'data_update',
                            'model': 'userprofile',
                            'action': 'theme_updated',
                            'theme': serializer.data['theme'],
                            'user_id': request.user.id
                        }
                    )
                    
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsManagerOrDeveloper]

    def get_queryset(self):
        qs = AuditLog.objects.all().select_related('target_user', 'performed_by').order_by('-created_at')
        target_user = self.request.query_params.get('target_user')
        if target_user:
            qs = qs.filter(target_user_id=target_user)
        return qs

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [DjangoModelPermissions]
    queryset = Employee.objects.none() # Needed for DjangoModelPermissions to work on ViewSet sometimes, or just use AllowAny/IsAuthenticated

    def list(self, request):
        total_employees = Employee.objects.filter(is_active=True, deleted_at__isnull=True).count()
        
        latest_run = PayrollRun.objects.order_by('-created_at').first()
        active_payroll = 0
        if latest_run:
            agg = PayrollEntry.objects.filter(run=latest_run).aggregate(total=Sum('net_pay'))
            active_payroll = agg['total'] or 0
            
        pending_requests = LeaveRequest.objects.filter(status='pending').count()
        
        today = date.today()
        present_today = AttendanceRecord.objects.filter(date=today, status='present').count()
        attendance_percentage = (present_today / total_employees * 100) if total_employees > 0 else 0
        
        dept_distribution = Department.objects.annotate(employee_count=Count('employee')).values('name', 'employee_count')
        
        recent_activity = AuditLogSerializer(
            AuditLog.objects.select_related('target_user', 'performed_by').order_by('-created_at')[:5], 
            many=True
        ).data

        return Response({
            'total_employees': total_employees,
            'active_payroll': active_payroll,
            'pending_requests': pending_requests,
            'attendance_percentage': round(attendance_percentage, 1),
            'department_distribution': list(dept_distribution),
            'recent_activity': recent_activity,
            'monthly_trend': [ # Mock data for now
                {'month': 'Jan', 'amount': 3500000},
                {'month': 'Feb', 'amount': 4000000},
                {'month': 'Mar', 'amount': 3800000},
                {'month': 'Apr', 'amount': 5000000},
                {'month': 'May', 'amount': 4800000},
                {'month': 'Jun', 'amount': 6200000},
            ]
        })
