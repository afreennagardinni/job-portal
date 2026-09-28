from django.urls import path
from . import views

urlpatterns = [
    path('post-job/', views.post_job, name='post_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job-detail/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job-list/', views.job_list, name='job_list'),  # Add this line
    path('apply-job/<int:job_id>/', views.apply_job, name='apply_job'),  # Add this line
    path('my-applications/', views.my_applications, name='my_applications'),  # Add this line
]