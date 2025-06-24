from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User, Role, Authority, Department

class UserRegistrationForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), empty_label="Select Role")
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Select Department")
    mentor = forms.ModelChoiceField(queryset=User.objects.none(), required=False, label="Assign Mentor")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'mentor', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields['role'].queryset = Role.objects.filter(company=company)
            self.fields['department'].queryset = Department.objects.filter(company=company)

            # Initialize mentor field as empty
            self.fields['mentor'].queryset = User.objects.none()

            if 'role' in self.data:
                try:
                    role_id = int(self.data.get('role'))
                    role = Role.objects.get(id=role_id, company=company)
                    if role.report_to:
                        self.fields['mentor'].queryset = User.objects.filter(
                            role=role.report_to,
                            company=company,
                            is_active=True
                        )
                except (ValueError, Role.DoesNotExist):
                    pass
            elif self.instance.pk and self.instance.role:
                if self.instance.role.report_to:
                    self.fields['mentor'].queryset = User.objects.filter(
                        role=self.instance.role.report_to,
                        company=company,
                        is_active=True
                    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        mentor = cleaned_data.get('mentor')
        # Removed the junior-specific validation to allow mentors for all roles
        return cleaned_data

class UserEditForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'mentor')

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if self.company:
            self.fields['department'].queryset = Department.objects.filter(company=self.company)
            self.fields['role'].queryset = Role.objects.filter(company=self.company)

            # Default: empty mentor list
            self.fields['mentor'].queryset = User.objects.none()

            # Logic to restrict mentors based on the role's report_to value
            if self.instance and self.instance.role and self.instance.role.report_to:
                self.fields['mentor'].queryset = User.objects.filter(
                    role=self.instance.role.report_to,
                    company=self.company,
                    is_active=True
                )


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

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if self.company:
            self.fields['report_to'].queryset = Role.objects.filter(company=self.company)
            self.fields['authorities'].queryset = Authority.objects.all()




class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
