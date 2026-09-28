from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import UserRegistrationForm
from jobs.models import Job, Category
from applications.models import Application
import os

User = get_user_model()

# ============= REGISTRATION =============
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# ============= CUSTOM LOGOUT =============
def custom_logout(request):
    """Custom logout view to handle logout properly"""
    logout(request)
    return redirect('login')


# ============= DASHBOARD (Combined for all users) =============
@login_required
def dashboard(request):
    """Combined dashboard for all user types"""
    
    # ===== SUPERUSER/ADMIN DASHBOARD =====
    if request.user.is_superuser:
        # Statistics
        total_users = User.objects.count()
        total_employers = User.objects.filter(user_type='employer').count()
        total_job_seekers = User.objects.filter(user_type='job_seeker').count()
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        total_applications = Application.objects.count()
        
        # Recent users
        recent_users = User.objects.order_by('-date_joined')[:5]
        
        # Recent jobs
        recent_jobs = Job.objects.order_by('-created_at')[:5]
        
        # Applications by status
        pending_apps = Application.objects.filter(status='pending').count()
        reviewed_apps = Application.objects.filter(status='reviewed').count()
        shortlisted_apps = Application.objects.filter(status='shortlisted').count()
        hired_apps = Application.objects.filter(status='hired').count()
        
        # Last 7 days activity
        last_week = timezone.now() - timedelta(days=7)
        new_users_week = User.objects.filter(date_joined__gte=last_week).count()
        new_jobs_week = Job.objects.filter(created_at__gte=last_week).count()
        new_apps_week = Application.objects.filter(applied_at__gte=last_week).count()
        
        context = {
            'total_users': total_users,
            'total_employers': total_employers,
            'total_job_seekers': total_job_seekers,
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'recent_users': recent_users,
            'recent_jobs': recent_jobs,
            'pending_apps': pending_apps,
            'reviewed_apps': reviewed_apps,
            'shortlisted_apps': shortlisted_apps,
            'hired_apps': hired_apps,
            'new_users_week': new_users_week,
            'new_jobs_week': new_jobs_week,
            'new_apps_week': new_apps_week,
            'is_admin': True,  # Flag for admin template
        }
        return render(request, 'accounts/dashboard.html', context)
    
    # ===== EMPLOYER DASHBOARD =====
    elif request.user.user_type == 'employer':
        jobs = Job.objects.filter(employer=request.user)
        applications = Application.objects.filter(job__in=jobs)
        context = {
            'jobs': jobs,
            'applications': applications,
            'total_jobs': jobs.count(),
            'total_applications': applications.count(),
            'is_employer': True,
        }
        return render(request, 'accounts/dashboard.html', context)
    
    # ===== JOB SEEKER DASHBOARD =====
    elif request.user.user_type == 'job_seeker':
        applications = Application.objects.filter(applicant=request.user)
        context = {
            'applications': applications,
            'total_applications': applications.count(),
            'is_job_seeker': True,
        }
        return render(request, 'accounts/dashboard.html', context)
    
    # ===== DEFAULT/OTHER =====
    else:
        context = {}
        return render(request, 'accounts/dashboard.html', context)


# ============= ADMIN DASHBOARD (Separate URL if needed) =============
@login_required
def admin_dashboard(request):
    """Admin Dashboard with real statistics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Basic counts
    total_users = User.objects.count()
    total_employers = User.objects.filter(user_type='employer').count()
    total_job_seekers = User.objects.filter(user_type='job_seeker').count()
    total_admins = User.objects.filter(is_superuser=True).count()
    
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    inactive_jobs = total_jobs - active_jobs
    
    total_applications = Application.objects.count()
    total_categories = Category.objects.count()
    
    # Application status counts
    pending_apps = Application.objects.filter(status='pending').count()
    reviewed_apps = Application.objects.filter(status='reviewed').count()
    shortlisted_apps = Application.objects.filter(status='shortlisted').count()
    interview_apps = Application.objects.filter(status='interview').count()
    hired_apps = Application.objects.filter(status='hired').count()
    rejected_apps = Application.objects.filter(status='rejected').count()
    
    # Calculate percentages
    total_apps = total_applications or 1
    pending_percent = round((pending_apps / total_apps) * 100)
    reviewed_percent = round((reviewed_apps / total_apps) * 100)
    shortlisted_percent = round((shortlisted_apps / total_apps) * 100)
    interview_percent = round((interview_apps / total_apps) * 100)
    hired_percent = round((hired_apps / total_apps) * 100)
    rejected_percent = round((rejected_apps / total_apps) * 100)
    
    # User percentages
    total_users_count = total_users or 1
    seeker_percent = round((total_job_seekers / total_users_count) * 100)
    employer_percent = round((total_employers / total_users_count) * 100)
    admin_percent = round((total_admins / total_users_count) * 100)
    
    # Job type counts
    fulltime_jobs = Job.objects.filter(job_type='full_time').count()
    parttime_jobs = Job.objects.filter(job_type='part_time').count()
    remote_jobs = Job.objects.filter(job_type='remote').count()
    contract_jobs = Job.objects.filter(job_type='contract').count()
    
    # Recent items
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_applications = Application.objects.order_by('-applied_at')[:5]
    
    # Top categories
    top_categories = Category.objects.annotate(
        job_count=Count('jobs')
    ).order_by('-job_count')[:5]
    
    # Last 7 days activity
    last_week = timezone.now() - timedelta(days=7)
    new_users_week = User.objects.filter(date_joined__gte=last_week).count()
    new_jobs_week = Job.objects.filter(created_at__gte=last_week).count()
    new_apps_week = Application.objects.filter(applied_at__gte=last_week).count()
    
    context = {
        'total_users': total_users,
        'total_employers': total_employers,
        'total_job_seekers': total_job_seekers,
        'total_admins': total_admins,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'total_categories': total_categories,
        'pending_apps': pending_apps,
        'reviewed_apps': reviewed_apps,
        'shortlisted_apps': shortlisted_apps,
        'interview_apps': interview_apps,
        'hired_apps': hired_apps,
        'rejected_apps': rejected_apps,
        'pending_percent': pending_percent,
        'reviewed_percent': reviewed_percent,
        'shortlisted_percent': shortlisted_percent,
        'interview_percent': interview_percent,
        'hired_percent': hired_percent,
        'rejected_percent': rejected_percent,
        'seeker_percent': seeker_percent,
        'employer_percent': employer_percent,
        'admin_percent': admin_percent,
        'fulltime_jobs': fulltime_jobs,
        'parttime_jobs': parttime_jobs,
        'remote_jobs': remote_jobs,
        'contract_jobs': contract_jobs,
        'recent_users': recent_users,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'top_categories': top_categories,
        'new_users_week': new_users_week,
        'new_jobs_week': new_jobs_week,
        'new_apps_week': new_apps_week,
        'current_date': timezone.now(),
    }
    return render(request, 'accounts/admin_dashboard.html', context)


# ============= ACCOUNT DELETION =============
@login_required
def delete_account(request):
    """View to handle account deletion"""
    user = request.user
    
    if request.method == 'POST':
        # Get password confirmation
        password = request.POST.get('password')
        
        # Verify password
        if user.check_password(password):
            # Store username for success message
            username = user.username
            
            # Delete user's resume files if any
            if user.user_type == 'job_seeker':
                applications = Application.objects.filter(applicant=user)
                for application in applications:
                    if application.resume:
                        if os.path.isfile(application.resume.path):
                            os.remove(application.resume.path)
            
            # Delete user's profile picture if exists
            if user.profile_picture:
                if os.path.isfile(user.profile_picture.path):
                    os.remove(user.profile_picture.path)
            
            # Delete user's jobs if employer
            if user.user_type == 'employer':
                jobs = Job.objects.filter(employer=user)
                for job in jobs:
                    # Delete related applications first
                    Application.objects.filter(job=job).delete()
                jobs.delete()
            
            # Logout the user first
            logout(request)
            
            # Delete the user account
            user.delete()
            
            messages.success(request, f'Account "{username}" has been permanently deleted. We\'re sorry to see you go!')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account not deleted.')
            return redirect('delete_account')
    
    return render(request, 'accounts/delete_account.html', {'user': user})


@login_required
def confirm_delete_account(request):
    """Confirmation page before deletion"""
    return render(request, 'accounts/confirm_delete.html')


# ============= ACCOUNT DEACTIVATION =============
@login_required
def deactivate_account(request):
    """Alternative: Deactivate instead of permanent delete"""
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.info(request, 'Your account has been deactivated. You can reactivate by contacting support.')
        return redirect('home')
    
    return render(request, 'accounts/deactivate.html')