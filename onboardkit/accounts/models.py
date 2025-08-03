from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Authority(models.Model):
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class Role(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
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
        return f"{self.name} ({self.company.name})"


class Department(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    mentor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name()} - {self.username} ({self.role.name if self.role else 'No Role'})"

    def has_authority(self, code):
        return self.role and self.role.has_authority(code)

    def is_mentor(self):
        return User.objects.filter(mentor=self).exists()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
