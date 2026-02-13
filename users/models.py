from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class Role(models.Model):
    """User roles as per BRD specification"""
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True, choices=[
        ('Administrator', 'Administrator'),
        ('Doctor', 'Doctor'),
        ('Lab', 'Lab'),
        ('Viewer', 'Viewer'),
    ])
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.role_name

class Permission(models.Model):
    """System permissions as per BRD specification"""
    permission_id = models.AutoField(primary_key=True)
    permission_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return self.permission_name

class RolePermission(models.Model):
    """Role-Permission relationships as per BRD specification"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'permission')

    def __str__(self):
        return f"{self.role.role_name} - {self.permission.permission_name}"

class AdminEmailControl(models.Model):
    """Admin email control table as per BRD specification"""
    control_id = models.AutoField(primary_key=True)
    admin_email = models.EmailField(unique=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'admin_email_control'

    def __str__(self):
        return f"{self.admin_email} ({'Primary' if self.is_primary else 'Secondary'})"

class UserManager(BaseUserManager):
    """Custom manager for User model"""

    def create_user(self, email, full_name, password=None, role=None, create_by=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not full_name:
            raise ValueError('Full name is required')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            role_id=role,
            create_by=create_by,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'Active')
        
        # Validate that superuser flags are not being overridden to False
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')

        # Get or create admin role
        admin_role, created = Role.objects.get_or_create(
            role_name='Administrator',
            defaults={'description': 'System Administrator with full access'}
        )

        return self.create_user(
            email=email,
            full_name=full_name,
            password=password,
            role=admin_role,
            **extra_fields
        )

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model as per BRD specification"""
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, db_column='pass_hash')  # Django handles password hashing
    role_id = models.ForeignKey(Role, on_delete=models.PROTECT, null=True)
    create_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    create_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
        ('Disabled', 'Disabled'),
    ], default='Active')

    # Additional security fields as per BRD
    is_verified = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Django admin fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def has_perm(self, perm, obj=None):
        """Check if user has a specific permission"""
        # Superusers always have all permissions
        if self.is_superuser:
            return True
        if self.role_id:
            return RolePermission.objects.filter(
                role=self.role_id,
                permission__permission_name=perm
            ).exists()
        return False

    def has_perms(self, perm_list, obj=None):
        """Check if user has all permissions in list"""
        # Superusers always have all permissions
        if self.is_superuser:
            return True
        # Fetch user's permission set once to avoid N+1 queries
        if self.role_id:
            user_perms = self.get_all_permissions()
            return all(perm in user_perms for perm in perm_list)
        return False

    def get_all_permissions(self, obj=None):
        """Get all permissions for this user"""
        if self.role_id:
            return set(RolePermission.objects.filter(
                role=self.role_id
            ).values_list('permission__permission_name', flat=True))
        return set()

    @property
    def is_admin(self):
        return self.role_id and self.role_id.role_name == 'Administrator'

    @property
    def is_doctor(self):
        return self.role_id and self.role_id.role_name == 'Doctor'

    @property
    def is_lab(self):
        return self.role_id and self.role_id.role_name == 'Lab'

    @property
    def is_viewer(self):
        return self.role_id and self.role_id.role_name == 'Viewer'

    def is_locked(self):
        """Check if account is currently locked"""
        if self.lock_until and timezone.now() < self.lock_until:
            return True
        return False

    def reset_failed_attempts(self):
        """Reset failed attempts counter"""
        self.failed_attempts = 0
        self.lock_until = None
        self.save(update_fields=['failed_attempts', 'lock_until'])

    def increment_failed_attempts(self):
        """Increment failed attempts and lock if necessary"""
        self.failed_attempts += 1
        if self.failed_attempts >= 5:
            self.lock_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save(update_fields=['failed_attempts', 'lock_until'])


class RefreshToken(models.Model):
    """Refresh tokens for session management as per BRD specification"""
    token_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    revoked = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'refresh_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"RefreshToken for {self.user.email} - {'Revoked' if self.revoked else 'Active'}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordResetToken(models.Model):
    """Password reset tokens as per BRD specification"""
    reset_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"PasswordResetToken for {self.user.email} - {'Used' if self.used else 'Active'}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class EmailVerificationToken(models.Model):
    """Email verification tokens as per BRD specification"""
    verification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']

    def __str__(self):
        return f"EmailVerificationToken for {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class OTPCode(models.Model):
    """OTP codes for 2FA as per BRD specification"""
    otp_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    otp_code = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'otp_codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTPCode for {self.user.email} - {'Used' if self.used else 'Active'}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class LoginAttempt(models.Model):
    """Login attempts for security monitoring as per BRD specification"""
    attempt_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='login_attempts')
    email_attempted = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    success = models.BooleanField()
    attempt_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'login_attempts'
        ordering = ['-attempt_time']

    def __str__(self):
        user_email = self.user.email if self.user else self.email_attempted
        return f"LoginAttempt for {user_email} - {'Success' if self.success else 'Failed'}"
