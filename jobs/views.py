from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, Category
from applications.models import Application

# ============= EMPLOYER FUNCTIONS =============

@login_required
def post_job(request):
    if request.user.user_type != 'employer':
        messages.error(request, 'Only employers can post jobs!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        location = request.POST.get('location')
        job_type = request.POST.get('job_type')
        experience_level = request.POST.get('experience_level')
        salary_min = request.POST.get('salary_min')
        salary_max = request.POST.get('salary_max')
        application_deadline = request.POST.get('application_deadline')
        
        # Get category if selected
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        # Create job
        Job.objects.create(
            title=title,
            company=company,
            employer=request.user,
            category=category,
            description=description,
            requirements=requirements,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            salary_min=salary_min if salary_min else None,
            salary_max=salary_max if salary_max else None,
            application_deadline=application_deadline,
            is_active=True
        )
        
        messages.success(request, 'Job posted successfully!')
        return redirect('my_jobs')
    
    categories = Category.objects.all()
    return render(request, 'jobs/post_job.html', {
        'categories': categories,
        'job_types': Job.JOB_TYPES,
        'experience_levels': Job.EXPERIENCE_LEVELS
    })


@login_required
def my_jobs(request):
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied!')
        return redirect('dashboard')
    
    jobs = Job.objects.filter(employer=request.user).order_by('-created_at')
    return render(request, 'jobs/my_jobs.html', {'jobs': jobs})


@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        category_id = request.POST.get('category')
        
        if category_id:
            try:
                job.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                job.category = None
        else:
            job.category = None
            
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.location = request.POST.get('location')
        job.job_type = request.POST.get('job_type')
        job.experience_level = request.POST.get('experience_level')
        job.salary_min = request.POST.get('salary_min') if request.POST.get('salary_min') else None
        job.salary_max = request.POST.get('salary_max') if request.POST.get('salary_max') else None
        job.application_deadline = request.POST.get('application_deadline')
        job.save()
        
        messages.success(request, 'Job updated successfully!')
        return redirect('my_jobs')
    
    categories = Category.objects.all()
    return render(request, 'jobs/edit_job.html', {
        'job': job,
        'categories': categories,
        'job_types': Job.JOB_TYPES,
        'experience_levels': Job.EXPERIENCE_LEVELS
    })


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, employer=request.user)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('my_jobs')
    
    return render(request, 'jobs/delete_job.html', {'job': job})


@login_required
def job_list(request):
    # Get all active jobs
    jobs = Job.objects.filter(is_active=True)
    
    # Search query (simple search - not multi-keyword as requested)
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query) |
            Q(location__icontains=search_query)
        ).distinct()
    
    # Filter by job type
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Order by newest first
    jobs = jobs.order_by('-created_at')
    
    context = {
        'jobs': jobs,
        'job_types': Job.JOB_TYPES,
        'search_query': search_query,
        'selected_job_type': job_type,
        'selected_location': location
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Increment view count
    job.views_count += 1
    job.save()
    
    has_applied = False
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied
    })


@login_required
def apply_job(request, job_id):
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can apply for jobs!')
        return redirect('job_list')
    
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if already applied
    existing_application = Application.objects.filter(job=job, applicant=request.user).exists()
    
    if existing_application:
        messages.warning(request, 'You have already applied for this job!')
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        resume = request.FILES.get('resume')
        expected_salary = request.POST.get('expected_salary')
        
        Application.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            resume=resume,
            expected_salary=expected_salary if expected_salary else None,
            status='pending'
        )
        
        messages.success(request, 'Application submitted successfully!')
        return redirect('my_applications')
    
    return render(request, 'jobs/apply_job.html', {'job': job})


@login_required
def my_applications(request):
    if request.user.user_type != 'job_seeker':
        messages.error(request, 'Access denied!')
        return redirect('dashboard')
    
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    
    return render(request, 'jobs/my_applications.html', {'applications': applications})