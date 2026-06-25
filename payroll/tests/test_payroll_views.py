import pytest
from rest_framework import status
from payroll.models import SalaryComponent, EmployeeSalaryStructure, PayrollPeriod, PayrollRun, PayrollEntry

@pytest.fixture
def salary_comp(company):
    return SalaryComponent.objects.create(name='Base Pay', company=company, component_type='earning', calculation_method='fixed')

@pytest.fixture
def payroll_period(company):
    return PayrollPeriod.objects.create(company=company, start_date='2025-01-01', end_date='2025-01-31')

@pytest.mark.django_db
class TestSalaryComponentViewSet:
    def test_list_salary_components(self, auth_client, salary_comp):
        response = auth_client.get('/api/v1/payroll/salary-components/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_salary_component(self, auth_client, company):
        response = auth_client.post('/api/v1/payroll/salary-components/', {'name': 'Bonus', 'company': company.id, 'component_type': 'earning', 'calculation_method': 'fixed'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_salary_component(self, auth_client, salary_comp):
        response = auth_client.delete(f'/api/v1/payroll/salary-components/{salary_comp.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestEmployeeSalaryStructureViewSet:
    def test_list_salary_structures(self, auth_client, employee, salary_comp):
        EmployeeSalaryStructure.objects.create(employee=employee, component=salary_comp, amount=5000, effective_date='2025-01-01')
        response = auth_client.get('/api/v1/payroll/employee-salary-structures/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_salary_structure(self, auth_client, employee, salary_comp):
        response = auth_client.post('/api/v1/payroll/employee-salary-structures/', {'employee': employee.id, 'component': salary_comp.id, 'amount': 1000, 'effective_date': '2025-01-01'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_salary_structure(self, auth_client, employee, salary_comp):
        structure = EmployeeSalaryStructure.objects.create(employee=employee, component=salary_comp, amount=5000, effective_date='2025-01-01')
        response = auth_client.delete(f'/api/v1/payroll/employee-salary-structures/{structure.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestPayrollPeriodViewSet:
    def test_list_payroll_periods(self, auth_client, payroll_period):
        response = auth_client.get('/api/v1/payroll/payroll-periods/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_payroll_period(self, auth_client, company):
        response = auth_client.post('/api/v1/payroll/payroll-periods/', {'company': company.id, 'start_date': '2025-02-01', 'end_date': '2025-02-28'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_payroll_period(self, auth_client, payroll_period):
        response = auth_client.delete(f'/api/v1/payroll/payroll-periods/{payroll_period.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestPayrollRunViewSet:
    def test_list_payroll_runs(self, auth_client, payroll_period):
        PayrollRun.objects.create(period=payroll_period, status='DRAFT')
        response = auth_client.get('/api/v1/payroll/payroll-runs/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_payroll_run(self, auth_client, payroll_period):
        response = auth_client.post('/api/v1/payroll/payroll-runs/', {'period': payroll_period.id, 'status': 'DRAFT'})
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_payroll_run(self, auth_client, payroll_period):
        run = PayrollRun.objects.create(period=payroll_period, status='DRAFT')
        response = auth_client.delete(f'/api/v1/payroll/payroll-runs/{run.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
class TestPayrollEntryViewSet:
    def test_list_payroll_entries(self, auth_client, payroll_period, employee):
        run = PayrollRun.objects.create(period=payroll_period, status='DRAFT')
        PayrollEntry.objects.create(run=run, employee=employee, net_pay=5000)
        response = auth_client.get('/api/v1/payroll/payroll-entries/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_payroll_entry(self, auth_client, payroll_period, employee):
        run = PayrollRun.objects.create(period=payroll_period, status='DRAFT')
        response = auth_client.post('/api/v1/payroll/payroll-entries/', {'run': run.id, 'employee': employee.id, 'net_pay': 4000})
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_payroll_entry(self, auth_client, payroll_period, employee):
        run = PayrollRun.objects.create(period=payroll_period, status='DRAFT')
        entry = PayrollEntry.objects.create(run=run, employee=employee, net_pay=5000)
        response = auth_client.delete(f'/api/v1/payroll/payroll-entries/{entry.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
