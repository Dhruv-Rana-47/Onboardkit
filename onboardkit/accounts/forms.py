from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLES)
    mentor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='SENIOR'),
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
        if cleaned_data.get('role') == 'JUNIOR' and not cleaned_data.get('mentor'):
            raise forms.ValidationError("Mentor is required for junior roles")

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'mentor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mentor'].queryset = User.objects.filter(role='SENIOR')
        if self.instance.role != 'JUNIOR':
            self.fields['mentor'].widget = forms.HiddenInput()

class UserFilterForm(forms.Form):
    role = forms.ChoiceField(choices=[('', 'All Roles')] + list(User.ROLES), required=False)
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search users...'}))

