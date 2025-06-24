import django_filters
from django import forms
from django.db.models import Q
from .models import User, Role


class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search users...', 'class': 'form-control'})
    )
    
    role = django_filters.ModelChoiceFilter(
        queryset=Role.objects.none(),  # default; overridden in __init__
        label='Role',
        empty_label='All Roles',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['role']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.filters['role'].queryset = Role.objects.filter(company=company)

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
        widget=forms.TextInput(attrs={'placeholder': 'Search roles...', 'class': 'form-control'})
    )

    report_to = django_filters.ModelChoiceFilter(
        queryset=Role.objects.none(),  # default; overridden in __init__
        label='Reports To',
        empty_label='All',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Role
        fields = ['report_to']

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.filters['report_to'].queryset = Role.objects.filter(company=company)

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(authorities__label__icontains=value)
            ).distinct()
        return queryset
