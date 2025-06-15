from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django_filters.views import FilterView
from django.db.models import Q
from .models import User
from .forms import UserRegistrationForm, UserEditForm
from onboarding.models import OnboardingTemplate, UserTask
from messaging.models import Message
    
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from .tables import UserTable  # You'll need to create this
from .filters import UserFilter

# Admin User Management
def is_admin(user):
    return user.role == 'ADMIN'

# Authentication Views
@login_required
@user_passes_test(is_admin)
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Set user role based on form data
            role = form.cleaned_data.get('role')
            user.role = role
            user.save()
            
            # For junior users, assign mentor
            if role == 'JUNIOR':
                mentor = form.cleaned_data.get('mentor')
                user.mentor = mentor
                user.save()
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/register.html', {'form': form})

# Dashboard View (keep your existing version)
@login_required
def dashboard(request):
    context = {}
    user = request.user
    
    if user.role == 'ADMIN':
        users = User.objects.all().order_by('-date_joined')
        recent_tasks = UserTask.objects.all().order_by('-assigned_date')[:5]
        unread_messages = Message.objects.filter(recipient=user, read_at__isnull=True).count()
        
        context.update({
            'users': users,
            'recent_tasks': recent_tasks,
            'unread_messages': unread_messages,
        })
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    elif user.role == 'SENIOR':
        mentees = User.objects.filter(mentor=user, role='JUNIOR').select_related('profile') 
        templates = OnboardingTemplate.objects.filter(created_by=user)
        pending_tasks = UserTask.objects.filter(
            user__in=mentees,
            status__in=['PENDING', 'IN_PROGRESS']
        ).select_related('user').order_by('-due_date')
        
        context.update({
            'mentees': mentees,
            'templates': templates,
            'pending_tasks': pending_tasks,
            'unread_messages': Message.objects.filter(
                recipient=user,
                read_at__isnull=True
            ).count(),
            'last_login': user.last_login
        })
        return render(request, 'dashboard/mentor_dashboard.html', context)
        
    elif user.role == 'JUNIOR':
        tasks = user.tasks.all().order_by('-due_date')
        mentor = user.mentor
        unread_messages = Message.objects.filter(recipient=user, read_at__isnull=True).count()
        
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='COMPLETED').count()
        progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        context.update({
            'tasks': tasks,
            'mentor': mentor,
            'progress': progress,
            'unread_messages': unread_messages,
        })
        return render(request, 'dashboard/junior_dashboard.html', context)





class UserListView(FilterView, SingleTableView):
    model = User
    template_name = 'accounts/user_list.html'
    filterset_class = UserFilter
    table_class = UserTable
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().order_by('-date_joined')

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user with form's built-in password handling
            user = form.save(commit=False)
            
            # Handle additional fields
            if form.cleaned_data.get('role') == 'JUNIOR':
                user.mentor = form.cleaned_data.get('mentor')
            
            user.save()
            
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/add_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    tasks = user.tasks.all().order_by('-assigned_date')
    
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='COMPLETED').count()
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
    
    return render(request, 'accounts/user_detail.html', {
        'user': user,
        'tasks': tasks,
        'progress': progress,
    })

@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:user_detail', pk=user.pk)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/delete_user.html', {'user': user})


