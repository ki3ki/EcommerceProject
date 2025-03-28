from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# Custom User Manager to handle user and superuser creation
class UserManager(BaseUserManager):
    def create_user(self, email, username, full_name, phone, password=None):
        """Create and return a regular user with the given details."""
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if not full_name:
            raise ValueError("Users must have a full name")
        if not phone:
            raise ValueError("Users must have a phone number")

        # Normalize email and create user
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
            phone=phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, full_name, phone, password):
        """Create and return a superuser with admin permissions."""
        user = self.create_user(
            email=email,
            username=username,
            full_name=full_name,
            phone=phone,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Custom User Model extending AbstractBaseUser and PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    # Tracking fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    # User status and permissions
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "full_name", "phone"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Check if the user has specific permissions."""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Check if the user has permissions to view the app."""
        return self.is_superuser

    class Meta:
        ordering = ("email",)


# Address Model to store user addresses
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)  # Default address flag
    is_deleted = models.BooleanField(default=False)  # Soft delete flag

    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            # Set all other addresses of this user to non-default
            Address.objects.filter(user=self.user).update(is_default=False)
        elif not Address.objects.filter(user=self.user, is_default=True).exists():
            # If no default address exists for this user, make this one default
            self.is_default = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"

    class Meta:
        verbose_name_plural = "Addresses"
