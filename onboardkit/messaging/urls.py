from django.urls import path
from . import views
app_name = 'messaging'
urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent'),
    path('compose/', views.compose_message, name='compose_message'),
    path('compose/<int:recipient_id>/', views.compose_message, name='compose_message'),
    path('<int:pk>/', views.message_detail, name='message_detail'),
    path('<int:pk>/reply/', views.reply_message, name='reply_message'),
    path('<int:pk>/forward/', views.forward_message, name='forward'),
    path('<int:pk>/delete/', views.delete_message, name='delete_message'),
]