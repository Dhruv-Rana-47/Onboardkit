from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OnboardingTemplate, TemplateSection, UserTask, TemplateItem, TaskFeedback, TaskRating, User, KPI
from .forms import (
    OnboardingTemplateForm, TemplateSectionForm, TemplateItemForm,
    AssignTaskForm, TaskFilterForm, TaskForm, AssignTemplateForm, TaskRatingForm
)
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection
from accounts.utils import authority_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required

# ------------------ TEMPLATE VIEWS ------------------

@login_required
@authority_required("view_templates")
def template_list(request):
    templates = OnboardingTemplate.objects.filter(created_by=request.user)
    return render(request, 'onboarding/template_list.html', {'templates': templates})

@login_required
@authority_required("create_template")
def template_create(request):
    if request.method == 'POST':
        form = OnboardingTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, 'Template created successfully!')
            return redirect('onboarding:template_detail', pk=template.pk)
    else:
        form = OnboardingTemplateForm()
    return render(request, 'onboarding/template_form.html', {'form': form})

@login_required
@authority_required("view_templates")
def template_detail(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.user != template.created_by and not request.user.has_authority('view_templates'):
        messages.error(request, "You don't have permission to view this template")
        return redirect('onboarding:template_list')
    return render(request, 'onboarding/template_detail.html', {'template': template})

@login_required
@authority_required("edit_template")
def template_edit(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.method == 'POST':
        form = OnboardingTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template updated successfully!')
            return redirect('onboarding:template_detail', pk=template.pk)
    else:
        form = OnboardingTemplateForm(instance=template)
    return render(request, 'onboarding/template_form.html', {'form': form, 'template': template, 'editing': True})

@require_POST
@login_required
@authority_required("edit_template")
def template_delete(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.user != template.created_by and not request.user.has_authority('edit_template'):
        messages.error(request, "You don't have permission to delete this template")
        return redirect('onboarding:template_list')
    template.delete()
    messages.success(request, 'Template deleted successfully!')
    return redirect('onboarding:template_list')

# ------------------ SECTION VIEWS ------------------

@login_required
@authority_required("edit_template")
def section_create(request, template_pk):
    template = get_object_or_404(OnboardingTemplate, pk=template_pk)
    if request.method == 'POST':
        form = TemplateSectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.template = template
            section.save()
            messages.success(request, 'Section added successfully!')
            return redirect('onboarding:template_detail', pk=template.pk)
    else:
        form = TemplateSectionForm()
    return render(request, 'onboarding/section_form.html', {'form': form, 'template': template})

@login_required
@authority_required("edit_template")
def section_edit(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    if request.method == 'POST':
        form = TemplateSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('onboarding:template_detail', pk=section.template.pk)
    else:
        form = TemplateSectionForm(instance=section)
    return render(request, 'onboarding/section_form.html', {'form': form, 'template': section.template, 'editing': True})

@require_POST
@login_required
@authority_required("edit_template")
def section_delete(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    template_pk = section.template.pk
    if request.user != section.template.created_by and not request.user.has_authority('edit_template'):
        messages.error(request, "You don't have permission to delete this section")
    else:
        section.delete()
        messages.success(request, 'Section deleted successfully!')
    return redirect('onboarding:template_detail', pk=template_pk)

@require_POST
@login_required
@authority_required("edit_template")
def reorder_sections(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    section_ids = request.POST.getlist('section_ids[]')
    for index, section_id in enumerate(section_ids):
        TemplateSection.objects.filter(pk=section_id, template=template).update(order=index)
    return HttpResponse('Reordered', status=200)

# ------------------ ITEM VIEWS ------------------

@login_required
@authority_required("edit_template")
def item_create(request, section_pk):
    section = get_object_or_404(TemplateSection, pk=section_pk)
    if request.method == 'POST':
        form = TemplateItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.section = section
            item.save()
            messages.success(request, 'Item added successfully!')
            return redirect('onboarding:template_detail', pk=section.template.pk)
    else:
        form = TemplateItemForm()
    return render(request, 'onboarding/item_form.html', {'form': form, 'section': section})

@login_required
@authority_required("edit_template")
def item_edit(request, pk):
    item = get_object_or_404(TemplateItem, pk=pk)
    if request.method == 'POST':
        form = TemplateItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('onboarding:template_detail', pk=item.section.template.pk)
    else:
        form = TemplateItemForm(instance=item)
    return render(request, 'onboarding/item_form.html', {'form': form, 'section': item.section, 'editing': True})

@require_POST
@login_required
@authority_required("edit_template")
def item_delete(request, pk):
    item = get_object_or_404(TemplateItem, pk=pk)
    template_pk = item.section.template.pk
    if request.user != item.section.template.created_by and not request.user.has_authority('edit_template'):
        messages.error(request, "You don't have permission to delete this item")
    else:
        item.delete()
        messages.success(request, 'Item deleted successfully!')
    return redirect('onboarding:template_detail', pk=template_pk)

@require_POST
@login_required
@authority_required("edit_template")
def reorder_items(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    item_ids = request.POST.getlist('item_ids[]')
    for index, item_id in enumerate(item_ids):
        TemplateItem.objects.filter(pk=item_id, section=section).update(order=index)
    return HttpResponse('Reordered', status=200)

# ------------------ TASK VIEWS ------------------


@login_required
@authority_required("manage_tasks")
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, "Task created successfully.")
            return redirect('onboarding:task_detail', pk=task.pk)
    else:
        form = TaskForm(user=request.user)
        connection.close()
    return render(request, 'onboarding/task_create.html', {'form': form})

@login_required
@authority_required("manage_tasks")
def assign_task(request):
    if request.method == 'POST':
        form = AssignTaskForm(request.user, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, 'Task assigned successfully!')
            return redirect('onboarding:task_detail', pk=task.pk)
    else:
        form = AssignTaskForm(request.user)
    return render(request, 'onboarding/assign_task.html', {'form': form})

@login_required
@authority_required("manage_tasks")
def task_edit(request, pk):
    task = get_object_or_404(UserTask, pk=pk)
    if not (request.user == task.assigned_by or request.user.has_authority('manage_tasks')):
        raise PermissionDenied
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('onboarding:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'onboarding/task_edit.html', {'form': form, 'task': task})

@require_POST
@login_required
@authority_required("manage_tasks")
def task_delete(request, pk):
    task = get_object_or_404(UserTask, pk=pk)
    if not (request.user == task.assigned_by or request.user.has_authority('manage_tasks')):
        messages.error(request, "You don't have permission to delete this task")
        return redirect('onboarding:task_detail', pk=task.pk)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('onboarding:task_list')

@login_required
@authority_required("view_tasks")
def task_detail(request, pk):
    task = get_object_or_404(UserTask, pk=pk)
    if not (request.user in [task.user, task.assigned_by] or request.user.has_authority('view_tasks')):
        messages.error(request, "You don't have permission to view this task")
        return redirect('dashboard')
    
    related_tasks = task.user.tasks.exclude(pk=task.pk).order_by('-assigned_date')[:3]
    rating = getattr(task, 'rating', None)
    show_rating_form = request.user == task.assigned_by and request.user != task.user
    
    if request.method == 'POST':
        if 'complete_task' in request.POST and request.user == task.user and request.user.has_authority('complete_task'):
            task.status = 'COMPLETED'
            task.completed_date = timezone.now()
            task.save()
            messages.success(request, 'Task marked as completed!')
            return redirect('onboarding:task_detail', pk=task.pk)
        elif 'add_feedback' in request.POST and request.user != task.user and request.user.has_authority('give_feedback'):
            feedback = TaskFeedback(task=task, author=request.user, comment=request.POST.get('comment'))
            if 'attachment' in request.FILES:
                feedback.attachment = request.FILES['attachment']
            feedback.save()
            messages.success(request, 'Feedback submitted!')
            return redirect('onboarding:task_detail', pk=task.pk)
        elif 'submit_rating' in request.POST and show_rating_form and request.user.has_authority('rate_user'):
            if task.status != 'COMPLETED':
                messages.error(request, "You can only rate a completed task.")
                return redirect('onboarding:task_detail', pk=task.pk)
            form = TaskRatingForm(request.POST, task=task)
            if form.is_valid():
                TaskRating.objects.update_or_create(task=task, rated_by=request.user, defaults=form.cleaned_data)
                messages.success(request, 'Rating submitted!')
                return redirect('onboarding:task_detail', pk=task.pk)
    
    form = TaskRatingForm(instance=rating, task=task) if show_rating_form else None
    return render(request, 'onboarding/task_detail.html', {
        'task': task,
        'related_tasks': related_tasks,
        'rating': rating,
        'show_rating_form': show_rating_form,
        'rating_form': form
    })

@login_required
@authority_required("view_tasks")
def task_list(request):
    queryset = UserTask.objects.all().order_by('-assigned_date')
    filter_form = TaskFilterForm(request.GET or None)
    if filter_form.is_valid():
        queryset = filter_form.filter_queryset(queryset)
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'onboarding/task_list.html', {
        'tasks': page_obj,
        'filter_form': filter_form,
        'is_paginated': page_obj.has_other_pages()
    })

# ------------------ TEMPLATE ASSIGNMENT ------------------

@login_required
@authority_required("assign_template")
def assign_template(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.method == 'POST':
        form = AssignTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.template = template
            assignment.assigned_by = request.user
            try:
                assignment.save()
                create_tasks_from_template(assignment)
                messages.success(request, 'Template assigned successfully!')
                return redirect('onboarding:template_detail', pk=template.pk)
            except IntegrityError:
                messages.error(request, 'This template is already assigned to the selected user')
    else:
        form = AssignTemplateForm(user=request.user)
    return render(request, 'onboarding/assign_template.html', {'form': form, 'template': template})

def create_tasks_from_template(assignment):
    sections = list(assignment.template.sections.all())
    for section in sections:
        items = list(section.items.all())
        for item in items:
            UserTask.objects.create(
                user=assignment.assignee,
                assigned_by=assignment.assigned_by,
                template_item=item,
                due_date=assignment.due_date,
                status='NOT_STARTED'
            )

# ------------------ KPI DASHBOARD ------------------

@login_required
@authority_required("view_kpi")
def kpi_dashboard(request):
    user_kpis = KPI.objects.filter(user=request.user)
    total_kpi = user_kpis.aggregate(total=Sum('points'))['total'] or 0
    
    avg_points_per_task = user_kpis.aggregate(avg=Avg('points'))['avg'] or 0
    completion_rate = user_kpis.count() / max(1, request.user.tasks.count())
    on_time_rate = user_kpis.filter(was_late=False).count() / max(1, user_kpis.count())
    early_completion_rate = user_kpis.filter(was_early=True).count() / max(1, user_kpis.count())
    
    recent_kpis = user_kpis.filter(awarded_at__gte=timezone.now()-timezone.timedelta(days=30))
    recent_avg = recent_kpis.aggregate(avg=Avg('points'))['avg'] or 0
    
    mentee_kpis = None
    if request.user.has_authority('view_subordinates'):
        mentees = User.objects.filter(mentor=request.user)
        mentee_kpis = []
        for mentee in mentees:
            mentee_data = {
                'user': mentee,
                'total_kpi': KPI.objects.filter(user=mentee).aggregate(total=Sum('points'))['total'] or 0,
                'task_count': mentee.tasks.count(),
                'completed_count': mentee.tasks.filter(status='COMPLETED').count(),
                'avg_rating': TaskRating.objects.filter(task__user=mentee).aggregate(avg=Avg('rating'))['avg'] or 0,
                'on_time_rate': KPI.objects.filter(user=mentee, was_late=False).count() / 
                               max(1, KPI.objects.filter(user=mentee).count())
            }
            mentee_kpis.append(mentee_data)
        mentee_kpis.sort(key=lambda x: x['total_kpi'], reverse=True)
    
    return render(request, 'onboarding/kpi_dashboard.html', {
        'total_kpi': total_kpi,
        'avg_points_per_task': round(avg_points_per_task, 1),
        'completion_rate': round(completion_rate * 100, 1),
        'on_time_rate': round(on_time_rate * 100, 1),
        'early_completion_rate': round(early_completion_rate * 100, 1),
        'recent_avg': round(recent_avg, 1),
        'mentee_kpis': mentee_kpis,
        'kpi_history': list(user_kpis.order_by('-awarded_at')[:10]),
    })