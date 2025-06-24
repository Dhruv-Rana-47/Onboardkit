
from django.urls import path
from .views import (UserListView, add_user, user_detail, 
                   edit_user, delete_user, company_hierarchy,role_management, add_role, edit_role, delete_role,get_mentors_for_role,department_list, add_department, edit_department, delete_department)
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
    path('ajax/get-mentors/', get_mentors_for_role, name='get_mentors_for_role'),
    path('departments/', department_list, name='department_list'),
    path('departments/add/', add_department, name='add_department'),
    path('departments/<int:pk>/edit/', edit_department, name='edit_department'),
    path('departments/<int:pk>/delete/', delete_department, name='delete_department'),
    path('hierarchy/', company_hierarchy, name='company_hierarchy'),

]