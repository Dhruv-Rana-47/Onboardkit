from django.contrib import admin
from .models import Message, Attachment


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'sent_at', 'read_at', 'is_read')
    list_filter = ('sender', 'recipient', 'sent_at', 'read_at')
    search_fields = ('subject', 'body')
    date_hierarchy = 'sent_at'
    ordering = ('-sent_at',)

    def is_read(self, obj):
        return obj.read_at is not None
    is_read.boolean = True
    is_read.short_description = 'Read'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('message', 'file', 'uploaded_at')
    search_fields = ('message__subject',)
    raw_id_fields = ('message',)
