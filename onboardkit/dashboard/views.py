from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.models import User

@login_required
def dashboard(request):
    context = {}
    
    if request.user.role == 'ADMIN':
        users = User.objects.all()
        context['users'] = users
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    elif request.user.role == 'SENIOR':
        mentees = User.objects.filter(mentor=request.user, role='JUNIOR')
        context['mentees'] = mentees
        return render(request, 'dashboard/mentor_dashboard.html', context)
    
    elif request.user.role == 'JUNIOR':
        tasks = request.user.tasks.all()
        context['tasks'] = tasks
        return render(request, 'dashboard/junior_dashboard.html', context)