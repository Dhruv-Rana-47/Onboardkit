from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model, logout
from django.contrib import messages
from django_filters.views import FilterView
from django.db.models import Q
from .models import User, Role, Department
from .forms import UserRegistrationForm, UserEditForm, RoleForm, DepartmentForm
from onboarding.models import OnboardingTemplate, UserTask
from messaging.models import Message
from django_tables2 import SingleTableView
from django.http import HttpResponse, HttpResponseForbidden,JsonResponse
from .tables import UserTable, RoleTable
from .filters import UserFilter, RoleFilter
from django_tables2 import RequestConfig
from accounts.utils import authority_required
from collections import defaultdict



@login_required
def get_mentors_for_role(request):
    role_id = request.GET.get('role_id')
    if not role_id:
        return JsonResponse({'error': 'No role_id provided'}, status=400)

    try:
        role = Role.objects.get(id=role_id, company=request.user.company)
        if not role.report_to:
            return JsonResponse({'mentors': []})
            
        mentors = User.objects.filter(
            role=role.report_to, 
            company=request.user.company,
            is_active=True
        )
        data = [{'id': u.id, 'name': u.get_full_name() or u.username} for u in mentors]
        return JsonResponse({'mentors': data})
    except Role.DoesNotExist:
        return JsonResponse({'error': 'Invalid role_id'}, status=404)


# Dashboard View
@login_required
def dashboard(request):
    if not request.user.company or not request.user.company.is_active:
        logout(request)
        return HttpResponse("Company account suspended")
    user = request.user
    authorities = set(user.role.authorities.values_list('code', flat=True)) if user.role else set()

    context = {
        'user': user,
        'authorities': authorities,
        'unread_messages': Message.objects.filter(recipient=user, read_at__isnull=True).count(),
    }

    if 'view_mentor_info' in authorities:
        context['mentor'] = user.mentor if hasattr(user, 'mentor') else None

    if 'view_hierarchy' in authorities:
        mentees = User.objects.filter(mentor=user, company=user.company)
        for mentee in mentees:
            tasks = UserTask.objects.filter(user=mentee)
            total = tasks.count()
            completed = tasks.filter(status='COMPLETED').count()
            mentee.task_progress = int((completed / total) * 100) if total else 0
        context['mentees'] = mentees
        context['mentee_tasks'] = UserTask.objects.filter(user__in=mentees).select_related('user')

    if 'view_tasks' in authorities:
        user_tasks = UserTask.objects.filter(user=user)
        context['tasks'] = user_tasks
        context['pending_task_count'] = user_tasks.exclude(status='COMPLETED').count()

        if 'view_progress' in authorities:
            completed_tasks = user_tasks.filter(status='COMPLETED').count()
            context['progress'] = int((completed_tasks / user_tasks.count()) * 100) if user_tasks.count() else 0

    if 'view_templates' in authorities:
        context['templates'] = OnboardingTemplate.objects.filter(created_by=user)

    return render(request, 'dashboard/common_dashboard.html', context)



class UserListView(FilterView, SingleTableView):
    model = User
    template_name = 'accounts/user_list.html'
    filterset_class = UserFilter
    table_class = UserTable
    paginate_by = 10

    def get_queryset(self):
        return User.objects.filter(company=self.request.user.company).order_by('-date_joined')

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['company'] = self.request.user.company
        return kwargs

@login_required
@authority_required("create_user")
def add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, company=request.user.company)
        if form.is_valid():
            user = form.save(commit=False)
            user.company = request.user.company
            user.save()
            if form.cleaned_data.get('mentor'):
                user.mentor = form.cleaned_data.get('mentor')
                user.save()
            messages.success(request, f'User {user.username} created successfully!')
            return redirect('accounts:user_list')
    else:
        form = UserRegistrationForm(company=request.user.company)

    return render(request, 'accounts/add_user.html', {'form': form})


@login_required
@authority_required("view_users")
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk, company=request.user.company)
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
@authority_required("edit_user")
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk, company=request.user.company)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('accounts:user_detail', pk=user.pk)
    else:
        form = UserEditForm(instance=user, company=request.user.company)
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})


@login_required
@authority_required("edit_user")
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk, company=request.user.company)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('accounts:user_list')
    return render(request, 'accounts/delete_user.html', {'user': user})


@login_required
@authority_required("manage_roles")
def role_management(request):
    roles = Role.objects.filter(company=request.user.company)
    role_filter = RoleFilter(request.GET, queryset=roles, company=request.user.company)


    table = RoleTable(role_filter.qs)
    RequestConfig(request, paginate={"per_page": 10}).configure(table)

    if request.method == 'POST':
        form = RoleForm(request.POST, company=request.user.company)
        if form.is_valid():
            role = form.save(commit=False)
            role.company = request.user.company
            role.save()
            form.save_m2m()
            messages.success(request, 'Role added successfully!')
            return redirect('accounts:role_management')
    else:
        form = RoleForm(company=request.user.company)

    authorities = set(request.user.role.authorities.values_list('code', flat=True)) if request.user.role else set()

    return render(request, 'accounts/role_management.html', {
        'form': form,
        'filter': role_filter,
        'table': table,
        'authorities': authorities,
    })


@login_required
@authority_required("manage_roles")
def add_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST, company=request.user.company)
        if form.is_valid():
            role = form.save(commit=False)
            role.company = request.user.company
            role.save()
            form.save_m2m()
            messages.success(request, 'Role created successfully!')
            return redirect('accounts:role_management')
    else:
        form = RoleForm(company=request.user.company)

    return render(request, 'accounts/add_role.html', {'form': form})


@login_required
@authority_required("manage_roles")
def edit_role(request, pk):
    role = get_object_or_404(Role, pk=pk, company=request.user.company)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role, company=request.user.company)
        if form.is_valid():
            form.save()
            return redirect('accounts:role_management')
    else:
        form = RoleForm(instance=role, company=request.user.company)
    return render(request, 'accounts/edit_role.html', {'form': form, 'role': role})


@login_required
@authority_required("manage_roles")
def delete_role(request, pk):
    role = get_object_or_404(Role, pk=pk, company=request.user.company)
    if request.method == 'POST':
        role.delete()
        return redirect('accounts:role_management')
    return render(request, 'accounts/delete_role.html', {'role': role})


@login_required
@authority_required("manage_departments")
def department_list(request):
    departments = Department.objects.filter(company=request.user.company).order_by('name')
    return render(request, 'accounts/department_list.html', {'departments': departments})


@login_required
@authority_required("manage_departments")
def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.company = request.user.company
            department.save()
            messages.success(request, 'Department added successfully!')
            return redirect('accounts:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'accounts/add_department.html', {'form': form})


@login_required
@authority_required("manage_departments")
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk, company=request.user.company)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('accounts:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'accounts/edit_department.html', {'form': form, 'department': department})


@login_required
@authority_required("manage_departments")
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk, company=request.user.company)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('accounts:department_list')
    return render(request, 'accounts/delete_department.html', {'department': department})




@login_required
def company_hierarchy(request):
    """Render an interactive company organizational hierarchy"""
    
    # Security check
    if not request.user.company or not request.user.company.is_active:
        logout(request)
        return HttpResponse("Company account suspended")

    # Single optimized DB query
    roles = Role.objects.filter(company=request.user.company)\
                       .select_related('report_to')\
                       .prefetch_related('user_set')

    # Build hierarchy in-memory
    def build_hierarchy():
        role_children = defaultdict(list)
        roots = []
        
        # First pass - build parent-child relationships
        for role in roles:
            if role.report_to:
                role_children[role.report_to.id].append(role)
            else:
                roots.append(role)
        
        # Second pass - recursive tree builder
        def build_node(role):
            return {
                'role': role,
                'users': [user for user in role.user_set.all() if user.is_active],
                'children': [build_node(child) for child in sorted(
                    role_children.get(role.id, []),
                    key=lambda x: x.name  # Sort children alphabetically
                )]
            }
        
        return [build_node(root) for root in sorted(roots, key=lambda x: x.name)]

    context = {
        'hierarchy_tree': build_hierarchy(),
        # 'authorities': getattr(request, 'authorities', set()) , # Safe fallback
        'request': request,
        'user': request.user,
    }
    
    return render(request, 'accounts/company_hierarchy.html', context)