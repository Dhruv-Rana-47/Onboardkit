

from django.utils import timezone  # Add this import
from django.db import models
from accounts.models import User

class OnboardingTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    role = models.CharField(max_length=10, choices=User.ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class TemplateSection(models.Model):
    template = models.ForeignKey(OnboardingTemplate, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    def move_to(self, new_order):
        current_order = self.order
        if new_order > current_order:
            self.template.sections.filter(
                order__lte=new_order,
                order__gt=current_order
            ).update(order=models.F('order') - 1)
        else:
            self.template.sections.filter(
                order__lt=current_order,
                order__gte=new_order
            ).update(order=models.F('order') + 1)
        self.order = new_order
        self.save()

class TemplateItem(models.Model):
    ITEM_TYPES = [
        ('GUIDE', 'Learning Guide'),
        ('DOC', 'Document'),
        ('TOOL', 'Tool Setup'),
        ('TASK', 'Practical Task'),
    ]
    section = models.ForeignKey(TemplateSection, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    document = models.FileField(upload_to='onboarding_docs/', blank=True)
    expected_output = models.TextField(blank=True)  # For tasks
    expected_duration_new = models.DurationField(null=True, blank=True)


    order = models.IntegerField()

    def move_to(self, new_order):
        current_order = self.order
        if new_order > current_order:
            self.section.items.filter(
                order__lte=new_order,
                order__gt=current_order
            ).update(order=models.F('order') - 1)
        else:
            self.section.items.filter(
                order__lt=current_order,
                order__gte=new_order
            ).update(order=models.F('order') + 1)
        self.order = new_order
        self.save()


class UserTask(models.Model):
    # Keep all your existing fields
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NOT_STARTED'
    )
    
    # Add this new field above your existing fields
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ]
    priority = models.CharField(
        max_length=6,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        help_text="Task priority level"
    )

    # Keep all your existing fields below
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    # ... rest of your current fields ...
    template_item = models.ForeignKey(TemplateItem, on_delete=models.CASCADE, null=True, blank=True)
    custom_task = models.TextField(null=True, blank=True)  # For non-template tasks
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='PENDING')
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-assigned_date']


    # Add these properties at the bottom of the class
    @property
    def is_overdue(self):
        return self.due_date and self.due_date < timezone.now().date() and self.status != 'COMPLETED'
    
    @property
    def days_remaining(self):
        if not self.due_date:
            return None
        delta = self.due_date - timezone.now().date()
        return delta.days

    def __str__(self):
        return f"{self.user.username} - {self.get_task_title()} (Priority: {self.priority})"
    
    def get_task_title(self):
        return self.template_item.title if self.template_item else self.custom_task
    @property
    def can_be_edited_by(self):
        def check(user):
            return user.is_authenticated and (
                user.is_admin 
                or getattr(self, 'assigned_by', None) == user 
        )
        return check
    
    
    @property
    def can_be_deleted_by(self):
        def check(user):
            return (
                user.is_admin() or 
                (user.is_senior() and user == self.assigned_by)
            )
        return check
# models.py
class TaskFeedback(models.Model):
    task = models.ForeignKey(UserTask, on_delete=models.CASCADE, related_name='feedbacks')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    attachment = models.FileField(upload_to='feedback_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class TemplateAssignment(models.Model):
    template = models.ForeignKey(OnboardingTemplate, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_templates')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('template', 'assignee')

    def __str__(self):
        return f"{self.template.name} -> {self.assignee.get_full_name()}"