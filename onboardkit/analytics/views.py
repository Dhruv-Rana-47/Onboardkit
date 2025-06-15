from pyexpat.errors import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Count, Avg,Q,F
from .forms import DateRangeForm
from accounts.models import User
from onboarding.models import UserTask

@login_required
def analytics_dashboard(request):
    if not request.user.is_admin and not request.user.is_mentor:
        messages.error(request, "You don't have permission to view analytics")
        return redirect('dashboard')
    
    form = DateRangeForm(request.GET or None)
    filters = {}
    
    if form.is_valid():
        if form.cleaned_data['start_date']:
            filters['assigned_date__gte'] = form.cleaned_data['start_date']
        if form.cleaned_data['end_date']:
            filters['assigned_date__lte'] = form.cleaned_data['end_date']
        if form.cleaned_data['user']:
            filters['user'] = form.cleaned_data['user']
    
    # Admin stats
    if request.user.is_admin:
        user_stats = User.objects.aggregate(
            total=Count('id'),
            admins=Count('id', filter=Q(role='ADMIN')),
            mentors=Count('id', filter=Q(role='SENIOR')),
            juniors=Count('id', filter=Q(role='JUNIOR'))
        )
        
        task_stats = UserTask.objects.filter(**filters).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED')),
            avg_completion_time=Avg(F('completed_date') - F('assigned_date'))
        )
    
    # Mentor stats
    elif request.user.is_mentor:
        mentees = User.objects.filter(mentor=request.user)
        filters['user__in'] = mentees
        
        task_stats = UserTask.objects.filter(**filters).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='COMPLETED'))
        )
        
        mentee_progress = []
        for mentee in mentees:
            tasks = mentee.tasks.filter(**filters)
            completed = tasks.filter(status='COMPLETED').count()
            mentee_progress.append({
                'mentee': mentee,
                'total': tasks.count(),
                'completed': completed,
                'percentage': (completed / tasks.count() * 100) if tasks.count() > 0 else 0
            })
    
    return render(request, 'analytics/dashboard.html', {
        'form': form,
        'user_stats': user_stats if request.user.is_admin else None,
        'task_stats': task_stats,
        'mentee_progress': mentee_progress if request.user.is_mentor else None
    })



@login_required
def user_progress_report(request):
    if not request.user.is_admin and not request.user.is_mentor:
        return redirect('dashboard')
    
    users = User.objects.all()
    if request.user.is_mentor:
        users = users.filter(mentor=request.user)
    
    progress_data = []
    for user in users:
        tasks = user.tasks.all()
        completed = tasks.filter(status='COMPLETED').count()
        progress_data.append({
            'user': user,
            'total_tasks': tasks.count(),
            'completed': completed,
            'percentage': (completed/tasks.count()*100) if tasks.count() > 0 else 0
        })
    
    return render(request, 'analytics/user_progress.html', {'progress_data': progress_data})

@login_required
def task_completion_report(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    
    tasks = UserTask.objects.values('assigned_by__username').annotate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='COMPLETED')))
    
    return render(request, 'analytics/task_completion.html', {'tasks': tasks})

@login_required
def onboarding_time_report(request):
    if not request.user.is_admin:
        return redirect('dashboard')
    
    times = UserTask.objects.filter(status='COMPLETED').annotate(
        duration=F('completed_date') - F('assigned_date')
    ).values('user__username').annotate(
        avg_time=Avg('duration')
    )
    
    return render(request, 'analytics/onboarding_time.html', {'times': times})