from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Using custom logout
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Account Management URLs
    path('delete-account/', views.delete_account, name='delete_account'),
    path('confirm-delete/', views.confirm_delete_account, name='confirm_delete'),
    path('deactivate/', views.deactivate_account, name='deactivate_account'),
]