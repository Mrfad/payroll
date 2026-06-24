from django.contrib import admin
from .models import DeviceConfiguration, RawAttendanceLog

@admin.register(DeviceConfiguration)
class DeviceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'device_type', 'ip_address', 'is_active', 'last_sync_time')
    list_filter = ('company', 'device_type', 'is_active')
    search_fields = ('name', 'ip_address', 'serial_number')

@admin.register(RawAttendanceLog)
class RawAttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'external_id', 'punch_time', 'direction', 'status')
    list_filter = ('device', 'status', 'direction', 'punch_time')
    search_fields = ('external_id',)
    readonly_fields = ('device', 'external_id', 'punch_time', 'direction', 'raw_data', 'status', 'processed_at')
    
    def has_add_permission(self, request):
        # Prevent manual addition of raw logs from admin
        return False
