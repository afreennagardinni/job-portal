from django.db import models
from django.utils import timezone
from datetime import date
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead / Manager'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='jobs')
    
    # Description
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True, default='')
    
    # Location & Type
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    
    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Skills & Vacancies
    skills_required = models.TextField(help_text="Comma separated skills", blank=True)
    vacancies = models.PositiveIntegerField(default=1)
    
    # Dates
    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('job_detail', args=[str(self.id)])
    
    def total_applications(self):
        """Return total number of applications for this job"""
        return self.applications.count()
    
    def is_deadline_passed(self):
        """Check if application deadline has passed"""
        return self.application_deadline < date.today()
    
    def get_status_display(self):
        """Return job status (Active/Expired) based on deadline"""
        if self.is_deadline_passed():
            return "Expired"
        return "Active" if self.is_active else "Inactive"
    
    def get_salary_range(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min} - ${self.salary_max}"
        elif self.salary_min:
            return f"From ${self.salary_min}"
        elif self.salary_max:
            return f"Up to ${self.salary_max}"
        return "Negotiable"
    
    class Meta:
        ordering = ['-created_at']