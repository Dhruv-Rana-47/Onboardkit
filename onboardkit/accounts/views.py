from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django_filters.views import FilterView
from django.db.models import Q
from .models import User, Role
from .forms import UserRegistrationForm, UserEditForm, RoleForm
from onboarding.models import OnboardingTemplate, UserTask
from messaging.models import Message
    
from django_tables2 import SingleTableView
from django_filters.views import FilterView
from .tables import UserTable  # You'll need to create this
from .filters import UserFilter
from django.http import HttpResponse


from .filters import RoleFilter
from django_tables2 import RequestConfig

from .tables import RoleTable
from django_tables2 import RequestConfig

# Admin User Management
def is_admin(user):
    return user.role and user.role.name.upper() == 'ADMIN'

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
    
    user = request.user

    # ✅ Admin dashboard
    if user.is_admin():
        users = User.objects.all().order_by('-date_joined')
        recent_tasks = UserTask.objects.all().order_by('-assigned_date')[:5]
        unread_messages = Message.objects.filter(recipient=user, read_at__isnull=True).count()
        return render(request, 'dashboard/admin_dashboard.html', {
            'users': users,
            'recent_tasks': recent_tasks,
            'unread_messages': unread_messages,
        })

    # ✅ Authority-based context
    authorities = set(user.role.authorities.values_list('code', flat=True))
    context = {
        'user': user,
        'authorities': authorities,
        'unread_messages': Message.objects.filter(recipient=user, read_at__isnull=True).count(),
    }

    # ✅ My Mentor
    if 'view_mentor_info' in authorities:
        context['mentor'] = user.mentor if hasattr(user, 'mentor') else None

    # ✅ Mentees (for mentors/seniors)
    mentees = []
    if 'view_hierarchy' in authorities:
        mentees = User.objects.filter(mentor=user, role__name='JUNIOR')
        for mentee in mentees:
            tasks = UserTask.objects.filter(user=mentee)
            total = tasks.count()
            completed = tasks.filter(status='COMPLETED').count()
            mentee.task_progress = int((completed / total) * 100) if total else 0
        context['mentees'] = mentees

    # ✅ My Tasks
    user_tasks = UserTask.objects.filter(user=user)
    if 'view_tasks' in authorities:
        context['tasks'] = user_tasks
        context['pending_task_count'] = user_tasks.exclude(status='COMPLETED').count()
        context['completed_task_count'] = user_tasks.filter(status='COMPLETED').count()

    # ✅ Mentees' Tasks (if mentor/senior)
    if 'view_hierarchy' in authorities:
        mentee_users = User.objects.filter(mentor=user)
        mentee_tasks = UserTask.objects.filter(user__in=mentee_users).select_related('user')
        context['mentee_tasks'] = mentee_tasks

    # ✅ Templates
    if 'view_templates' in authorities:
        context['templates'] = OnboardingTemplate.objects.filter(created_by=user)

    # ✅ Progress (user's own task completion)
    if 'view_progress' in authorities:
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='COMPLETED').count()
        context['progress'] = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    print(context)

    return render(request, 'dashboard/common_dashboard.html', context)




class UserListView(FilterView, SingleTableView):
    model = User
    template_name = 'accounts/user_list.html'
    filterset_class = UserFilter
    table_class = UserTable
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().order_by('-date_joined')

@login_required
def add_user(request):
    if not request.user.role.has_authority('create_user'):
        return HttpResponse("Unauthorized", status=403)

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('role') and form.cleaned_data['role'].name == 'JUNIOR':
                user.mentor = form.cleaned_data.get('mentor')
            user.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/add_user.html', {'form': form})


@login_required
# @user_passes_test(is_admin)
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
# @user_passes_test(is_admin)
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
# @user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/delete_user.html', {'user': user})



@login_required
@user_passes_test(is_admin)
def role_management(request):
    roles = Role.objects.all().order_by('-created_at')
    role_filter = RoleFilter(request.GET, queryset=roles)
    table = RoleTable(role_filter.qs)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role added successfully!')
            return redirect('accounts:role_management')
    else:
        form = RoleForm()

    return render(request, 'accounts/role_management.html', {
        'form': form,
        'filter': role_filter,
        'table': table
    })




@login_required
@user_passes_test(is_admin)
def add_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully!')
            return redirect('accounts:role_management')
    else:
        form = RoleForm()
    
    return render(request, 'accounts/add_role.html', {'form': form})    

@login_required
@user_passes_test(is_admin)
def edit_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('accounts:role_management')
    else:
        form = RoleForm(instance=role)
    return render(request, 'accounts/edit_role.html', {'form': form, 'role': role})


@login_required
@user_passes_test(is_admin)
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('accounts:role_management')
    return render(request, 'accounts/delete_role.html', {'role': role})