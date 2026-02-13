from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email only
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Find user by email only
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None

        # Check password and user status
        if (user.check_password(password) and
            self.user_can_authenticate(user) and
            user.status == 'Active'):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
