
from django.urls import path
from .views import (UserListView, add_user, user_detail, 
                   edit_user, delete_user, role_management, add_role, edit_role, delete_role)
app_name = 'accounts'
urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('add/', add_user, name='add_user'),
    path('<int:pk>/', user_detail, name='user_detail'),
    path('<int:pk>/edit/', edit_user, name='edit_user'),
    path('<int:pk>/delete/', delete_user, name='delete_user'),
    path('roles/', role_management, name='role_management'),
    path('roles/add/', add_role, name='add_role'),
    path('roles/<int:pk>/edit/', edit_role, name='edit_role'),
    path('roles/<int:pk>/delete/', delete_role, name='delete_role'),
]