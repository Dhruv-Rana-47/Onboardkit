from django import forms
from .models import (
    OnboardingTemplate,
    TemplateSection,
    TemplateItem,
    UserTask,
    User,
    TemplateAssignment,
)


class OnboardingTemplateForm(forms.ModelForm):
    class Meta:
        model = OnboardingTemplate
        fields = ("name", "description", "role")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


# Enhance your existing forms with better field configuration
class TemplateSectionForm(forms.ModelForm):
    class Meta:
        model = TemplateSection
        fields = ("title", "order")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {"order": "Section Number"}


class TemplateItemForm(forms.ModelForm):
    class Meta:
        model = TemplateItem
        fields = [
            "title",
            "item_type",
            "content",
            "video_url",
            "document",
            "expected_output",
            "expected_duration_new",
            "order",
        ]

        widgets = {
            "item_type": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "video_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://example.com/video",
                }
            ),
            "document": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "expected_duration": forms.NumberInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class AssignTaskForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For mentors: only show their mentees
        if user.role == "SENIOR":
            self.fields["user"].queryset = User.objects.filter(mentor=user)
        # Admins can assign to anyone
        elif user.role == "ADMIN":
            self.fields["user"].queryset = User.objects.exclude(role="ADMIN")

    class Meta:
        model = UserTask
        fields = ("user", "template_item", "custom_task", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "custom_task": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get("template_item") and not cleaned_data.get(
            "custom_task"
        ):
            raise forms.ValidationError(
                "You must select a template item or enter a custom task"
            )
        return cleaned_data


class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "All Statuses")]
        + list(UserTask.STATUS_CHOICES),  # Convert tuple to list
        required=False,
        label="Status",
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Users",
        label="Assigned To",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can add dynamic queryset filtering here if needed
        self.fields["assigned_to"].queryset = User.objects.filter(is_active=True)

    def filter_queryset(self, queryset):
        if self.cleaned_data["status"]:
            queryset = queryset.filter(status=self.cleaned_data["status"])
        if self.cleaned_data["assigned_to"]:
            queryset = queryset.filter(user=self.cleaned_data["assigned_to"])
        return queryset


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # ✅ 1. Pre-evaluate MENTOR's mentees as choices
        if user and user.role == "SENIOR":
            mentees = list(User.objects.filter(mentor=user))
            self.fields["user"].choices = [(u.pk, str(u)) for u in mentees]

        # ✅ 2. Pre-evaluate template_items to avoid lazy query
        items = list(TemplateItem.objects.all())
        self.fields["template_item"].choices = [("", "---------")] + [
            (i.pk, str(i.title)) for i in items
        ]

        # ✅ 3. Set priority choices directly (already a constant list)
        self.fields["priority"].choices = [("", "Select Priority")] + list(
            UserTask.PRIORITY_CHOICES
        )

        # ✅ 4. Only show 'status' if allowed
        if not (
            user.is_admin
            or (
                hasattr(self.instance, "assigned_by")
                and user == self.instance.assigned_by
            )
        ):
            self.fields.pop("status", None)

    class Meta:
        model = UserTask
        fields = [
            "user",
            "template_item",
            "custom_task",
            "due_date",
            "priority",
            "status",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class AssignTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["assignee"].queryset = User.objects.filter(
                is_active=True,
                role__in=["JUNIOR", "INTERN"],  # Only assign to juniors/interns
            ).exclude(pk=user.pk)

    class Meta:
        model = TemplateAssignment
        fields = ("assignee", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
