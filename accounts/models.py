from django.contrib.auth.models import AbstractUser 
from django.db import models 
 
class User(AbstractUser): 
    USER_TYPES = ( 
        ('job_seeker', 'Job Seeker'), 
        ('employer', 'Employer'), 
        ('admin', 'Admin'), 
    ) 
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='job_seeker') 
    phone_number = models.CharField(max_length=15, blank=True) 
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
 
    def __str__(self): 
        return f"{self.username} - {self.user_type}" 
