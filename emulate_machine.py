import os
import sys
import json
import urllib.request
import django
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj.settings')
django.setup()

from device.models import DeviceConfiguration
from payroll.models import Company

def main():
    if len(sys.argv) < 3:
        print("Usage: python emulate_machine.py <employee_id> <in/out>")
        print("Example: python emulate_machine.py EMP001 in")
        sys.exit(1)

    employee_id = sys.argv[1]
    direction = sys.argv[2].lower()

    if direction not in ['in', 'out']:
        print("Error: Direction must be 'in' or 'out'")
        sys.exit(1)

    print(f"Emulating machine punch for Employee: {employee_id}, Direction: {direction}")

    # Ensure we have at least one company
    company = Company.objects.first()
    if not company:
        print("Error: No company found in the database. Please create one first.")
        sys.exit(1)

    # Get or create a fake device
    device, created = DeviceConfiguration.objects.get_or_create(
        name="Main Entrance Scanner",
        device_type="zkteco_emulated",
        company=company,
        defaults={
            "ip_address": "192.168.1.100",
            "is_active": True,
            "api_token": "11111111-1111-1111-1111-111111111111"
        }
    )

    if created:
        print(f"Created emulated device: {device.name}")

    now = timezone.now()
    
    # Send HTTP request to Django server so that WebSockets are triggered properly
    # from within the running web server process
    url = "http://127.0.0.1:8000/api/v1/device/push/"
    payload = json.dumps({
        "external_id": employee_id,
        "punch_time": now.isoformat(),
        "direction": direction,
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Device-Token", str(device.api_token))
    
    try:
        response = urllib.request.urlopen(req)
        if response.status == 201:
            print(f"Success! Sent via HTTP API. Raw log created at {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print("The Flutter app should update in real-time.")
        else:
            print(f"Failed to push log. Status code: {response.status}")
    except urllib.error.URLError as e:
        print(f"HTTP Error: Could not connect to Django server at {url}.")
        print("Ensure the Django development server (python manage.py runserver) is running on port 8000.")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
