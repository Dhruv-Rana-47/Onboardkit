import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User
from .forms import forms

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search users...'})
    )
    
    role = django_filters.ChoiceFilter(
        choices=[('', 'All Roles')] + list(User.ROLES),
        empty_label='All Roles'
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