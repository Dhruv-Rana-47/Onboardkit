from django import forms
from .models import Message
from accounts.models import User

class MessageForm(forms.ModelForm):
    cc = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )

    def __init__(self, sender, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only allow users from the same company
        same_company_users = User.objects.filter(company=sender.company)

        # Mentor (if exists)
        mentor = [sender.mentor] if sender.mentor else []

        # Direct mentees
        mentees = list(User.objects.filter(mentor=sender))

        allowed_users = list(set(mentor + mentees))

        # Final allowed users (intersection with same company, just in case)
        allowed_users = [user for user in allowed_users if user in same_company_users]

        self.fields['recipient'].queryset = User.objects.filter(id__in=[u.id for u in allowed_users])
        self.fields['cc'].queryset = User.objects.filter(id__in=[u.id for u in allowed_users])

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Message
        fields = ('recipient', 'subject', 'body', 'cc')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Type your message here...'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject'}),
        }


class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Type your reply here...'
            }),
        }