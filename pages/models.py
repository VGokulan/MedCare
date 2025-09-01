# pages/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None   # remove username
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)  # ✅ this is new

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()


class Admin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)  # store hashed password

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email