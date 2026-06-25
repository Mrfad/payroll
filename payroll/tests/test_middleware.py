import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from payroll.middleware import CurrentUserMiddleware, ApiLoggingMiddleware
from django.http import HttpResponse

@pytest.fixture
def get_response():
    def _get_response(request):
        return HttpResponse("OK")
    return _get_response

@pytest.mark.django_db
class TestMiddlewares:
    def test_current_user_middleware_authenticated(self):
        user = User.objects.create_user('mw_user', 'mw@test.com', 'pw')
        request = RequestFactory().get('/api/v1/payroll/companies/')
        request.user = user
        
        from payroll.middleware import get_current_user, get_request_source

        def custom_get_response(req):
            assert get_current_user() == user
            assert get_request_source().startswith('API')
            return HttpResponse("OK")

        middleware = CurrentUserMiddleware(custom_get_response)
        middleware(request)

    def test_api_logging_middleware(self, get_response):
        from django.contrib.auth.models import AnonymousUser
        request = RequestFactory().get('/api/v1/payroll/companies/')
        request.user = AnonymousUser()
        middleware = ApiLoggingMiddleware(get_response)
        response = middleware(request)
        assert response.status_code == 200
