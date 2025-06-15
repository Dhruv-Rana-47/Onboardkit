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
        users = User.objects.exclude(pk=sender.pk)
        self.fields['recipient'].queryset = users
        self.fields['cc'].queryset = users
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