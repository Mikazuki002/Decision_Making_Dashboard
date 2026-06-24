from django.contrib import admin
from .models import Employee, Attendance, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'last_name', 'first_name', 'department', 'position', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('employee_id', 'first_name', 'last_name', 'position')
    ordering = ('last_name', 'first_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'status')
    list_filter = ('date', 'employee__department')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    date_hierarchy = 'date'
    ordering = ('-date',)
