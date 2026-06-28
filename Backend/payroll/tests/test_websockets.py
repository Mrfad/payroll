# Backend\payroll\tests\test_websockets.py
import pytest
from channels.testing import WebsocketCommunicator
from companies.models import Company
from prj.asgi import application


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_payroll_sync_consumer():
    # 1. Connect to the websocket
    communicator = WebsocketCommunicator(application, "/ws/updates/")
    connected, subprotocol = await communicator.connect()
    assert connected

    # 2. Trigger a save signal manually since it's an async test
    # Wait, in pytest-django async tests, ORM access needs to be sync_to_async
    from asgiref.sync import sync_to_async

    # Create a company which should trigger the post_save signal
    @sync_to_async
    def create_company():
        return Company.objects.create(name="WebSocket Test Company")

    await create_company()

    # 3. Receive the broadcasted messages from the websocket
    responses = []
    responses.append(await communicator.receive_json_from())
    try:
        # Depending on signals, AuditLog might also be created, sending another message.
        responses.append(await communicator.receive_json_from(timeout=1))
    except Exception:
        pass

    models_received = [r.get("model") for r in responses]
    assert "Company" in models_received

    company_resp = next(r for r in responses if r.get("model") == "Company")
    assert company_resp["type"] == "update"
    assert company_resp["action"] == "create"

    # 4. Disconnect
    await communicator.disconnect()
