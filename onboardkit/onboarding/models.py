from django.db import models
from django.utils import timezone
from django.conf import settings
from accounts.models import User, Role

# ---------------------- OnboardingTemplate & Related ----------------------

class OnboardingTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
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
            self.template.sections.filter(order__gt=current_order, order__lte=new_order).update(order=models.F('order') - 1)
        else:
            self.template.sections.filter(order__gte=new_order, order__lt=current_order).update(order=models.F('order') + 1)
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
    expected_output = models.TextField(blank=True)
    expected_duration_new = models.DurationField(null=True, blank=True)
    order = models.IntegerField()

    def move_to(self, new_order):
        current_order = self.order
        if new_order > current_order:
            self.section.items.filter(order__gt=current_order, order__lte=new_order).update(order=models.F('order') - 1)
        else:
            self.section.items.filter(order__gte=new_order, order__lt=current_order).update(order=models.F('order') + 1)
        self.order = new_order
        self.save()

# ----------------------------- User Task & KPI -----------------------------

class UserTask(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REVIEWED', 'Reviewed'),
    )

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    template_item = models.ForeignKey(TemplateItem, on_delete=models.CASCADE, null=True, blank=True)
    custom_task = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='MEDIUM')
    kpi_points = models.PositiveIntegerField(default=0, help_text="Points earned upon completion of this task")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.user.username} - {self.get_task_title()} (Priority: {self.priority})"

    def get_task_title(self):
        return self.template_item.title if self.template_item else self.custom_task

    @property
    def is_overdue(self):
        return self.due_date and self.due_date < timezone.now().date() and self.status != 'COMPLETED'

    @property
    def days_remaining(self):
        if not self.due_date:
            return None
        return (self.due_date - timezone.now().date()).days

    @property
    def can_be_edited_by(self):
        def check(user):
            return user.is_authenticated and (user.is_admin or self.assigned_by == user)
        return check

    @property
    def can_be_deleted_by(self):
        def check(user):
            return user.is_admin() or (user.is_senior() and user == self.assigned_by)
        return check

   
    def calculate_kpi_points(self):
        """Calculate dynamic KPI points based on multiple factors"""
        base_points = {
            'HIGH': 10,
            'MEDIUM': 6,
            'LOW': 4
        }.get(self.priority, 5)  # Default to 5 if priority not set
        
        # Calculate time-based bonuses/penalties
        time_factor = 1.0
        
        # Early completion bonus (up to 20% bonus)
        if self.completed_date and self.due_date:
            days_early = (self.due_date - self.completed_date.date()).days
            if days_early > 0:
                time_factor += min(0.2, days_early * 0.05)  # 5% per day early, max 20%
        
        # Late completion penalty (up to 30% penalty)
        elif self.is_overdue:
            days_late = (timezone.now().date() - self.due_date).days
            time_factor -= min(0.3, days_late * 0.05)  # 5% per day late, max 30%
        
        # Rating multiplier (1.0-1.3 based on rating)
        rating_multiplier = 1.0
        if hasattr(self, 'rating'):
            rating_multiplier = 1.0 + (self.rating.rating / 20)  # 1.0 for 1 star, 1.3 for 5 stars
        
        # Task complexity factor (based on item type)
        complexity_factor = {
            'GUIDE': 0.8,   # Reading is easier
            'DOC': 0.9,     # Document review
            'TOOL': 1.1,    # Tool setup is more complex
            'TASK': 1.2     # Practical tasks are most complex
        }.get(self.template_item.item_type if self.template_item else 'GUIDE', 1.0)
        
        # Calculate final points
        final_points = base_points * time_factor * rating_multiplier * complexity_factor
        
        # Ensure points are within reasonable bounds
        return max(1, min(20, round(final_points)))

    def save(self, *args, **kwargs):
        """Override save to update KPI points when task is completed"""
        is_new_completion = False
        
        if self.pk:
            previous = UserTask.objects.get(pk=self.pk)
            is_new_completion = previous.status != 'COMPLETED' and self.status == 'COMPLETED'
        
        super().save(*args, **kwargs)
        
        if is_new_completion:
            self.kpi_points = self.calculate_kpi_points()
            self.save(update_fields=['kpi_points'])
            
            # Create or update KPI record
            KPI.objects.update_or_create(
                user=self.user,
                task=self,
                defaults={
                    'points': self.kpi_points,
                    'completion_time': self.completed_date - self.assigned_date,
                    'was_early': self.due_date and self.completed_date.date() < self.due_date,
                    'was_late': self.is_overdue
                }
            )


class KPI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpis')
    task = models.ForeignKey(UserTask, on_delete=models.CASCADE, related_name='kpi')
    points = models.PositiveIntegerField()
    awarded_at = models.DateTimeField(auto_now_add=True)
    completion_time = models.DurationField(null=True, blank=True)
    was_early = models.BooleanField(default=False)
    was_late = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'task')
    
    @property
    def efficiency_score(self):
        """Calculate efficiency score (0-100) based on completion time vs expected"""
        if not self.completion_time or not self.task.template_item:
            return None
        
        expected_duration = self.task.template_item.expected_duration_new
        if not expected_duration:
            return None
        
        ratio = self.completion_time.total_seconds() / expected_duration.total_seconds()
        return min(100, max(0, round(100 * (1 / ratio))))  # Lower is better
# ----------------------------- Other Models -----------------------------

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


class TaskRating(models.Model):
    task = models.OneToOneField(UserTask, on_delete=models.CASCADE, related_name='rating')
    rated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    rated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'rated_by')

    def __str__(self):
        return f"{self.rated_by} rated {self.task} - {self.rating} stars"





