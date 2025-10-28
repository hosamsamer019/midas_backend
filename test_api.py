import os
import django
import requests

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from rest_framework_simplejwt.tokens import AccessToken
from users.models import User

# Get the first user and generate token
user = User.objects.first()
if user:
    token = str(AccessToken.for_user(user))
    print(f"Generated token: {token}")
    
    response = requests.get('http://127.0.0.1:8000/api/bacteria/', headers={'Authorization': f'Bearer {token}'})
    
    print(response.status_code)
    print(response.json())
else:
    print("No user found in database")
