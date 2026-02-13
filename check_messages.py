import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from messaging.models import Message
from users.models import User

# Get all users
users = User.objects.all()
print('Users:')
for u in users:
    print(f'  {u.user_id}: {u.email}')

# Get recent messages
print()
messages = Message.objects.all().order_by('-id')[:10]
print(f'Total messages: {Message.objects.count()}')
print()
for msg in messages:
    sender_id = msg.sender.user_id if msg.sender else None
    recipient_id = msg.recipient.user_id if msg.recipient else None
    sender_email = msg.sender.email if msg.sender else 'None'
    recipient_email = msg.recipient.email if msg.recipient else 'None'
    print(f'Message {msg.id}:')
    print(f'  Sender: {sender_id} ({sender_email})')
    print(f'  Recipient: {recipient_id} ({recipient_email})')
    print(f'  Subject: {msg.subject}')
    print()
