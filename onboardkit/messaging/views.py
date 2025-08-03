
from datetime import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Message,User
from .forms import MessageForm, MessageReplyForm
from django.core.paginator import Paginator
from django.conf import settings
from django.core.paginator import Paginator
from django.conf import settings
from django.utils import timezone  # Correct import
from django.core.exceptions import PermissionDenied


@login_required
def inbox(request):
    # Get messages with sender info to reduce queries
    messages = Message.objects.filter(
        recipient=request.user
    ).select_related('sender').order_by('-sent_at')
    
    # Pagination
    paginator = Paginator(messages, getattr(settings, 'MESSAGES_PER_PAGE', 10))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count unread messages (for the entire inbox)
    unread_count = messages.filter(read_at__isnull=True).count()
    
    return render(request, 'messaging/inbox.html', {
        'page_obj': page_obj,          # Paginated messages
        'unread_count': unread_count,  # Total unread count
        'active_folder': 'inbox'       # For UI highlighting
    })

@login_required
def sent_messages(request):
    sent_messages = Message.objects.filter(sender=request.user).order_by('-sent_at')
    return render(request, 'messaging/sent_messages.html', {
        'sent_messages': sent_messages,
        'active_folder': 'sent'
    })
@login_required
def compose_message(request, recipient_id=None):
    recipient = None
    initial = {}
    
    # Handle recipient (support both URL param and GET param)
    if recipient_id:
        recipient = get_object_or_404(User, pk=recipient_id)
    elif 'to' in request.GET:
        try:
            recipient = User.objects.get(pk=request.GET['to'])
        except (User.DoesNotExist, ValueError):
            messages.error(request, "Invalid recipient specified")
            return redirect('messaging:compose_message')
    
    if recipient:
        initial['recipient'] = recipient
        initial['subject'] = f"Re: " if 'reply' in request.GET else ""

    if request.method == 'POST':
        form = MessageForm(request.user, request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('messaging:inbox')
    else:
        form = MessageForm(request.user, initial=initial)
    
    return render(request, 'messaging/compose_message.html', {
        'form': form,
        'recipient': recipient,
        'is_reply': 'reply' in request.GET
    })
@login_required
def message_detail(request, pk):
    message = get_object_or_404(
        Message.objects.select_related('sender', 'recipient'),
        Q(pk=pk),
        Q(recipient=request.user) | Q(sender=request.user)
    )
    
    if message.recipient == request.user and not message.read_at:
        message.read_at = timezone.now()
        message.save(update_fields=['read_at'])
    
    return render(request, 'messaging/message_detail.html', {
        'message': message,
        'can_reply': message.sender != request.user
    })


@login_required
def delete_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    
    # Verify the user has permission to delete (either sender or recipient)
    if request.user not in [message.sender, message.recipient]:
        raise PermissionDenied
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('messaging:inbox')
    
    return render(request, 'messaging/confirm_delete.html', {'message': message})

@login_required
def reply_message(request, pk):
    original = get_object_or_404(Message, pk=pk)
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.sender = request.user
            reply.recipient = original.sender
            reply.subject = f"Re: {original.subject}"
            reply.save()
            messages.success(request, 'Reply sent successfully!')
            return redirect('messaging:inbox')
    else:
        form = MessageReplyForm(initial={'body': f"\n\n---- Original Message ----\n{original.body}"})
    
    return render(request, 'messaging/reply_message.html', {
        'form': form,
        'original': original
    })

@login_required
def forward_message(request, pk):
    original = get_object_or_404(Message, pk=pk, sender=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.user, request.POST)
        if form.is_valid():
            forwarded_msg = form.save(commit=False)
            forwarded_msg.sender = request.user
            forwarded_msg.body = original.get_forward_body() + forwarded_msg.body 
            forwarded_msg.save()
             
            
            # Handle attachments if you implement them
            # forward_attachments(original, forwarded_msg)
            
            messages.success(request, 'Message forwarded successfully!')
            return redirect('messaging:sent')
    else:
        initial = {
            'subject': f"Fwd: {original.subject}",
            'body': "\n\n----- Original Message -----\n"
        }
        form = MessageForm(request.user, initial=initial)
    
    return render(request, 'messaging/forward_message.html', {
        'form': form,
        'original': original
    })

