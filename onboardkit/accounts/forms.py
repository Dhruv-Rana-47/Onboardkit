from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User,Role, Authority

class UserRegistrationForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Select Role")
    mentor = forms.ModelChoiceField(
        queryset=User.objects.filter(role__name='SENIOR'),
        required=False,
        label="Assign Mentor (for interns)"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'mentor', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mentor'].widget.attrs.update({'class': 'select2'})

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        mentor = cleaned_data.get('mentor')
        if role and role.name == 'JUNIOR' and not mentor:
            raise forms.ValidationError("Mentor is required for junior roles")


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'mentor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mentor'].queryset = User.objects.filter(role__name='Senior')
        if not self.instance.role or self.instance.role.name != 'Junior':
            self.fields['mentor'].widget = forms.HiddenInput()

class UserFilterForm(forms.Form):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, empty_label='All Roles')
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search users...'}))

class RoleForm(forms.ModelForm):
    authorities = forms.ModelMultipleChoiceField(
        queryset=Authority.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Authorities"
    )

    class Meta:
        model = Role
        fields = ['name', 'report_to', 'authorities', 'description']