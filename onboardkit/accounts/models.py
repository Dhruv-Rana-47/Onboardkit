from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin/HR'),
        ('SENIOR', 'Senior/Mentor'),
        ('JUNIOR', 'Junior/Intern'),
    )
    
    role = models.CharField(max_length=10, choices=ROLES)
    mentor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_senior(self):
        return self.role == 'SENIOR'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"