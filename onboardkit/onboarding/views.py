from django.http import HttpResponse
from django.utils import timezone  # Add this import
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import OnboardingTemplate, TemplateSection, UserTask,TemplateItem,TaskFeedback,TaskRating
from .forms import (OnboardingTemplateForm, TemplateSectionForm, 
                   TemplateItemForm, AssignTaskForm, TaskFilterForm,TaskForm,AssignTemplateForm,TaskRatingForm )
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError,connection
 



@login_required
def template_list(request):
    templates = OnboardingTemplate.objects.filter(created_by=request.user)
    return render(request, 'onboarding/template_list.html', {'templates': templates})

@login_required
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
def template_detail(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.user != template.created_by and not request.user.is_admin:
        messages.error(request, "You don't have permission to view this template")
        return redirect('onboarding:template_list')
    
    return render(request, 'onboarding/template_detail.html', {'template': template})

@login_required
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
    
    return render(request, 'onboarding/section_form.html', {
        'form': form,
        'template': template
    })

@login_required
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
    
    return render(request, 'onboarding/item_form.html', {
        'form': form,
        'section': section
    })

@login_required
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
def task_detail(request, pk):
    task = get_object_or_404(UserTask, pk=pk)

    if request.user not in [task.user, task.assigned_by] and not request.user.is_admin:
        messages.error(request, "You don't have permission to view this task")
        return redirect('dashboard')

    related_tasks = task.user.tasks.exclude(pk=task.pk).order_by('-assigned_date')[:3]
    rating = getattr(task, 'rating', None)

    # Only mentors can submit ratings
    show_rating_form = request.user == task.assigned_by and request.user != task.user

    if request.method == 'POST':
        if 'complete_task' in request.POST and request.user == task.user:
            task.status = 'COMPLETED'
            task.completed_date = timezone.now()
            task.save()
            messages.success(request, 'Task marked as completed!')
            return redirect('onboarding:task_detail', pk=task.pk)

        elif 'add_feedback' in request.POST and request.user != task.user:
            feedback = TaskFeedback(
                task=task,
                author=request.user,
                comment=request.POST.get('comment')
            )
            if 'attachment' in request.FILES:
                feedback.attachment = request.FILES['attachment']
            feedback.save()
            messages.success(request, 'Feedback submitted!')
            return redirect('onboarding:task_detail', pk=task.pk)

        elif 'submit_rating' in request.POST and show_rating_form:
            if task.status != 'COMPLETED':
                messages.error(request, "You can only rate a completed task.")
                return redirect('onboarding:task_detail', pk=task.pk)

            form = TaskRatingForm(request.POST, task=task)
            if form.is_valid():
                TaskRating.objects.update_or_create(
                    task=task,
                    rated_by=request.user,
                    defaults=form.cleaned_data
                )
                messages.success(request, 'Rating submitted!')
                return redirect('onboarding:task_detail', pk=task.pk)
        else:
            form = TaskRatingForm(instance=rating, task=task) if show_rating_form else None
    else:
        form = TaskRatingForm(instance=rating, task=task) if show_rating_form else None

    return render(request, 'onboarding/task_detail.html', {
        'task': task,
        'related_tasks': related_tasks,
        'rating': rating,
        'show_rating_form': show_rating_form,
        'rating_form': form,
    })


from django.core.paginator import Paginator

from django.core.paginator import Paginator
from .forms import TaskFilterForm

def task_list(request):
    queryset = UserTask.objects.all().order_by('-assigned_date')
    filter_form = TaskFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        queryset = filter_form.filter_queryset(queryset)
    
    # Pagination
    paginator = Paginator(queryset, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'filter_form': filter_form,
        'is_paginated': page_obj.has_other_pages()
    }
    return render(request, 'onboarding/task_list.html', context)

from django.db import reset_queries
@login_required
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
        connection.close()  # ✅ Prevent cursor reuse bug (PostgreSQL fix)

    return render(request, 'onboarding/task_create.html', {'form': form})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(UserTask, pk=pk)
    
    # Permission check - only assigner or admin can edit
    if request.user not in [task.assigned_by, request.user.is_admin]:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('onboarding:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'onboarding/task_edit.html', {
        'form': form,
        'task': task
    })

from django.views.decorators.http import require_POST


@require_POST
@login_required
def task_delete(request, pk):
    task = get_object_or_404(UserTask, pk=pk)
    
    # Permission logic
    can_delete = (
        request.user.is_admin() or  # Admins can delete anything
        (request.user.is_senior() and request.user == task.assigned_by)  # Mentors can delete their own tasks
    )
    
    if not can_delete:
        messages.error(request, "You don't have permission to delete this task")
        return redirect('onboarding:task_detail', pk=task.pk)
    
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('onboarding:task_list')


@login_required
def template_edit(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.user != template.created_by and not request.user.is_admin:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = OnboardingTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template updated successfully!')
            return redirect('onboarding:template_detail', pk=template.pk)
    else:
        form = OnboardingTemplateForm(instance=template)
    
    return render(request, 'onboarding/template_form.html', {
        'form': form,
        'template': template,
        'editing': True
    })

@require_POST
@login_required
def template_delete(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    if request.user != template.created_by and not request.user.is_admin:
        messages.error(request, "You don't have permission to delete this template")
        return redirect('onboarding:template_list')
    
    template.delete()
    messages.success(request, 'Template deleted successfully!')
    return redirect('onboarding:template_list')



# Add these to your existing views
@login_required
def section_edit(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    if request.user != section.template.created_by and not request.user.is_admin:
        raise PermissionDenied

    if request.method == 'POST':
        form = TemplateSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('onboarding:template_detail', pk=section.template.pk)
    else:
        form = TemplateSectionForm(instance=section)
    
    return render(request, 'onboarding/section_form.html', {
        'form': form,
        'template': section.template,
        'editing': True
    })

@require_POST
@login_required
def section_delete(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    template_pk = section.template.pk
    if request.user != section.template.created_by and not request.user.is_admin:
        messages.error(request, "You don't have permission to delete this section")
    else:
        section.delete()
        messages.success(request, 'Section deleted successfully!')
    return redirect('onboarding:template_detail', pk=template_pk)


@login_required
def item_edit(request, pk):
    item = get_object_or_404(TemplateItem, pk=pk)
    if request.user != item.section.template.created_by and not request.user.is_admin:
        raise PermissionDenied

    if request.method == 'POST':
        form = TemplateItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('onboarding:template_detail', pk=item.section.template.pk)
    else:
        form = TemplateItemForm(instance=item)
    
    return render(request, 'onboarding/item_form.html', {
        'form': form,
        'section': item.section,
        'editing': True
    })

@require_POST
@login_required
def item_delete(request, pk):
    item = get_object_or_404(TemplateItem, pk=pk)
    template_pk = item.section.template.pk
    if request.user != item.section.template.created_by and not request.user.is_admin:
        messages.error(request, "You don't have permission to delete this item")
    else:
        item.delete()
        messages.success(request, 'Item deleted successfully!')
    return redirect('onboarding:template_detail', pk=template_pk)


@require_POST
@login_required
def reorder_sections(request, pk):
    template = get_object_or_404(OnboardingTemplate, pk=pk)
    order_mapping = request.POST.getlist('order[]')
    for index, section_id in enumerate(order_mapping, start=1):
        section = template.sections.get(id=section_id)
        section.move_to(index)
    return HttpResponse('OK')

@require_POST
@login_required
def reorder_items(request, pk):
    section = get_object_or_404(TemplateSection, pk=pk)
    order_mapping = request.POST.getlist('order[]')
    for index, item_id in enumerate(order_mapping, start=1):
        item = section.items.get(id=item_id)
        item.move_to(index)
    return HttpResponse('OK')


@login_required
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
                # Generate tasks from template items
                create_tasks_from_template(assignment)
                messages.success(request, 'Template assigned successfully!')
                return redirect('onboarding:template_detail', pk=template.pk)
            except IntegrityError:
                messages.error(request, 'This template is already assigned to the selected user')
    else:
        form = AssignTemplateForm(user=request.user)
    
    return render(request, 'onboarding/assign_template.html', {
        'form': form,
        'template': template
    })


def create_tasks_from_template(assignment):
    sections = list(assignment.template.sections.all())  # Force evaluation
    for section in sections:
        items = list(section.items.all())  # Force evaluation
        for item in items:
            UserTask.objects.create(
                user=assignment.assignee,
                assigned_by=assignment.assigned_by,
                template_item=item,
                due_date=assignment.due_date,
                status='NOT_STARTED'
            )
