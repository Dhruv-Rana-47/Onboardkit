from django.db import models
from accounts.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    cc = models.ManyToManyField(User, related_name='cc_messages', blank=True)
    bcc = models.ManyToManyField(User, related_name='bcc_messages', blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.subject} - {self.sender} to {self.recipient}"
    
    def get_forward_body(self):
        return (
            f"\n\n-------- Forwarded Message --------\n"
            f"From: {self.sender.get_full_name()}\n"
            f"Date: {self.sent_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Subject: {self.subject}\n\n"
            f"{self.body}"
        )
    


    
class Attachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)