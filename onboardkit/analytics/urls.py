from django.urls import path
from .views import (analytics_dashboard, user_progress_report,
                   task_completion_report, onboarding_time_report)
app_name='analytics'
urlpatterns = [
    path('', analytics_dashboard, name='analytics_dashboard'),
    path('user-progress/', user_progress_report, name='user_progress_report'),
    path('task-completion/', task_completion_report, name='task_completion_report'),
    path('onboarding-time/', onboarding_time_report, name='onboarding_time_report'),
]