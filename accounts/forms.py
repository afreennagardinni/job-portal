from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from .models import User 
 
class UserRegistrationForm(UserCreationForm): 
    email = forms.EmailField(required=True) 
    user_type = forms.ChoiceField(choices=User.USER_TYPES, required=True) 
 
    class Meta: 
        model = User 
        fields = ['username', 'email', 'password1', 'password2', 'user_type', 'phone_number'] 
 
    def save(self, commit=True): 
        user = super().save(commit=False) 
        user.email = self.cleaned_data['email'] 
        if commit: 
            user.save() 
        return user 
