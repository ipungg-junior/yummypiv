from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from datetime import datetime
# import timezone

class UsersManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        # Buat user baru dengan menggunakan phone_number sebagai identitas unik
        if not username:
            raise ValueError('The username field must be set')
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # Buat superuser dengan menggunakan phone_number sebagai identitas unik

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        superuser = self.create_user(username, password, **extra_fields)
        superuser.role = 'root'
        superuser.save()
        return superuser

# Create your models here.
class Users(AbstractUser):
    ROLE_CHOICES = (
        ('root', 'Root'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('guest', 'Guest'),
    )
    id = models.AutoField(primary_key=True)
    username = models.CharField(null=False, blank=False, unique=True, max_length=21)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    number_phone = models.CharField(max_length=14, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'username'
    objects = UsersManager()

    def __str__(self):
        return self.username
    

class Services(models.Model):
    name = models.CharField(max_length=255)
    img_link = models.CharField(max_length=255)


class OwnerProfile(models.Model):
    info = models.CharField(max_length=255)
    img_link = models.CharField(max_length=255)
    content = models.CharField(max_length=255)


class Visitor(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    path = models.CharField(max_length=255, null=True, blank=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visit from {self.ip_address} at {self.visited_at}"
    

class Article(models.Model):
    # Menyimpan berita
    title = models.CharField(max_length=255)
    img_link = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ClientInbox(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=40, null=True, blank=True)
    phone_number = models.CharField(max_length=14, null=True, blank=True)
    message = models.CharField(max_length=120, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inbox {self.subject} - {self.phone_number}"

class Partner(models.Model):
    name = models.CharField(max_length=255)
    img_link = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Notification(models.Model):
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    until_date = models.DateTimeField()

    def __str__(self):
        return f"Notification {self.title}"
    
    
class Testimonials(models.Model):
    customer_name = models.CharField(max_length=255)
    img_link = models.CharField(max_length=255)
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name