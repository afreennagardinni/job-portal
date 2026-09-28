from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Application
from jobs.models import Job
from accounts.models import User

@login_required
def admin_applications(request):
    """Admin view to see all applications"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    job_filter = request.GET.get('job', '')
    search_query = request.GET.get('search', '')
    
    # Get all applications
    applications = Application.objects.select_related('job', 'applicant').all().order_by('-applied_at')
    
    # Apply filters
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    
    if search_query:
        applications = applications.filter(
            Q(applicant__username__icontains=search_query) |
            Q(job__title__icontains=search_query) |
            Q(job__company__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all jobs for filter dropdown
    jobs = Job.objects.all().order_by('title')
    
    # Status choices for filter
    status_choices = Application.STATUS_CHOICES
    
    context = {
        'applications': page_obj,
        'jobs': jobs,
        'status_choices': status_choices,
        'selected_status': status_filter,
        'selected_job': job_filter,
        'search_query': search_query,
    }
    return render(request, 'applications/admin_applications.html', context)


@login_required
def admin_application_detail(request, pk):
    """Admin view to see application details and update status"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        # Update application status
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES).keys():
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}')
            return redirect('admin_application_detail', pk=application.pk)
    
    context = {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'applications/admin_application_detail.html', context)


@login_required
def admin_bulk_update_status(request):
    """Admin view to bulk update application statuses"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('bulk_status')
        
        if application_ids and new_status:
            updated = Application.objects.filter(id__in=application_ids).update(status=new_status)
            messages.success(request, f'{updated} applications updated to {dict(Application.STATUS_CHOICES).get(new_status)}')
        
        return redirect('admin_applications')
    
    return redirect('admin_applications')


@login_required
def admin_applications_by_job(request, job_id):
    """View applications for a specific job"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    job = get_object_or_404(Job, pk=job_id)
    applications = Application.objects.filter(job=job).order_by('-applied_at')
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'applications/admin_job_applications.html', context)