# from django.urls import path
# from . import views

# urlpatterns = [
#     # Templates
#     path('templates/', views.template_list, name='template_list'),
#     path('templates/add/', views.template_create, name='template_create'),
#     path('templates/<int:pk>/', views.template_detail, name='template_detail'),
#     path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
#     path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    
#     # Sections
#     path('templates/<int:template_pk>/sections/add/', views.section_create, name='section_create'),
#     path('sections/<int:pk>/edit/', views.section_edit, name='section_edit'),
#     path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),
    
#     # Items
#     path('sections/<int:section_pk>/items/add/', views.item_create, name='item_create'),
#     path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
#     path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),
    
#     # Tasks
#     path('tasks/', views.task_list, name='task_list'),
#     path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
#     path('tasks/<int:pk>/assign/', views.assign_task, name='assign_task'),
# ]


from django.urls import path
from .views import (template_list, template_create, template_detail,
                   section_create, item_create, task_detail,task_list,
                   assign_task,task_create,task_edit,task_delete,template_delete,
                   template_edit,section_delete,section_edit,item_delete,item_edit,
                reorder_items,reorder_sections,assign_template)
app_name='onboarding'
urlpatterns = [
    # Templates
    path('templates/', template_list, name='template_list'),
    path('templates/add/', template_create, name='template_create'),
    path('templates/<int:pk>/', template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', template_edit, name='template_edit'),
path('templates/<int:pk>/delete/', template_delete, name='template_delete'),
path('templates/<int:pk>/assign/', assign_template, name='assign_template'),
    # Sections
    path('templates/<int:template_pk>/sections/add/', section_create, name='section_create'),
    path('templates/<int:pk>/reorder-sections/', reorder_sections, name='reorder_sections'),
path('sections/<int:pk>/reorder-items/', reorder_items, name='reorder_items'),
    
    # Items
    path('sections/<int:section_pk>/items/add/', item_create, name='item_create'),
    # Add these URL patterns
path('sections/<int:pk>/edit/', section_edit, name='section_edit'),
path('sections/<int:pk>/delete/', section_delete, name='section_delete'),
path('items/<int:pk>/edit/', item_edit, name='item_edit'),
path('items/<int:pk>/delete/', item_delete, name='item_delete'),
    
    # Tasks
    path('tasks/', task_list, name='task_list'),
    path('tasks/<int:pk>/', task_detail, name='task_detail'),
    path('tasks/assign/', assign_task, name='assign_task'),
    path('tasks/create/', task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', task_delete, name='task_delete'),
]