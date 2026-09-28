from django.urls import path
from . import views

urlpatterns = [
    # Admin application URLs
    path('admin-applications/', views.admin_applications, name='admin_applications'),
    path('admin-application/<int:pk>/', views.admin_application_detail, name='admin_application_detail'),
    path('admin-bulk-update/', views.admin_bulk_update_status, name='admin_bulk_update'),
    path('admin-job-applications/<int:job_id>/', views.admin_applications_by_job, name='admin_job_applications'),
]