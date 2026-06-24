from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny, DjangoModelPermissions
from .permissions import IsOwnerOrAdmin
from .models import (
    Company, Department, Employee, Shift, BreakPolicy, OvertimePolicy,
    ShiftAssignment, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest,
    SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry
)
from .serializers import (
    CompanySerializer, DepartmentSerializer, EmployeeSerializer, ShiftSerializer,
    BreakPolicySerializer, OvertimePolicySerializer, ShiftAssignmentSerializer,
    AttendanceRecordSerializer, LeaveTypeSerializer, LeaveBalanceSerializer,
    LeaveRequestSerializer, SalaryComponentSerializer, EmployeeSalaryStructureSerializer,
    PayrollPeriodSerializer, PayrollRunSerializer, PayrollEntrySerializer,
    EmployeeEnrollmentSerializer
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
    permission_classes = [DjangoModelPermissions]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
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
    permission_classes = [IsOwnerOrAdmin]

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
    permission_classes = [IsOwnerOrAdmin]
