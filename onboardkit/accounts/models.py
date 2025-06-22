from django.contrib.auth.models import AbstractUser
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class Authority(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    report_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='sub_roles')
    authorities = models.ManyToManyField(Authority, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_authority(self, code):
        return self.authorities.filter(code=code).exists()

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    mentor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role.name if self.role else 'No Role'})"

    def is_admin(self):
        return self.role and self.role.name.upper() == 'ADMIN'

    def is_senior(self):
        return self.role and self.role.name.upper() == 'SENIOR'



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"