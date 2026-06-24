from django.urls import path
from . import views

app_name = 'dtr'

urlpatterns = [
    # Home -> attendance list
    path('', views.attendance_list, name='home'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/new/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/download.csv', views.download_employee_csv, name='employee_download'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('attendance/<int:pk>/in/', views.time_in, name='time_in'),
    path('attendance/<int:pk>/out/', views.time_out, name='time_out'),

    # Downloads
    path('download/csv/', views.download_csv, name='download_csv'),
    path('download/excel/', views.download_excel, name='download_excel'),

    # Dashboard + auto-updating visualizations
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/data.json', views.dashboard_data, name='dashboard_data'),
    path('dashboard/upload/', views.upload_excel, name='dashboard_upload'),
]
