import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User
from .forms import forms, Role

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search users...'})
    )
    
    role = django_filters.ModelChoiceFilter(
        queryset=Role.objects.all(),
        label='Role',
        empty_label='All Roles',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


    class Meta:
        model = User
        fields = ['role']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(username__icontains=value) |
                Q(email__icontains=value) |
                Q(first_name__icontains=value) |
                Q(last_name__icontains=value)
            )
        return queryset
    

class RoleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search roles...'})
    )

    report_to = django_filters.ModelChoiceFilter(
        queryset=Role.objects.all(),
        label='Reports To',
        empty_label='All',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Role
        fields = ['report_to']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(authorities__icontains=value)
        ) if value else queryset