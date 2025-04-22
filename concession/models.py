from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import date
from datetime import datetime
from django.utils.timezone import now
from django.conf import settings

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

class SignFormManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError("Users must have a username")
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class SignForm(AbstractBaseUser, PermissionsMixin):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name="signform_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="signform_users",
        blank=True
    )

    objects = SignFormManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    def __str__(self):
        return self.username

    #Candidate details Model
class details(models.Model):
        STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ]
        concession_id = models.AutoField(primary_key=True)  
        studentname = models.CharField(max_length=255)
        collegename = models.CharField(max_length=255)
        station1 = models.CharField(max_length=100)
        station2 = models.CharField(max_length=100)
        travel_class = models.CharField(max_length=50)
        validity=models.IntegerField(choices=[(1, "1 Month"), (3, "3 Months")])
        current_date = models.DateField()  # Ensure it stores as DateField
        valid_till_date = models.DateField() 
        login_id = models.ForeignKey(SignForm, on_delete=models.CASCADE)
        status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="pending")



class ApplicationStatus(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_process', 'Under Process'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    application_id = models.AutoField(primary_key=True)
    concession_id = models.ForeignKey('details', on_delete=models.CASCADE)
    submitted_date = models.DateField(auto_now_add=True)
    under_process_date = models.DateField(null=True, blank=True, default=None)
    accepted_date = models.DateField(null=True, blank=True, default=None)
    rejected_date = models.DateField(null=True, blank=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    login_id = models.ForeignKey(SignForm, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """Automatically update accepted/rejected dates based on the status of concession_id"""
        if self.concession_id:
            self.status = self.concession_id.status  # Sync status with details model

            if self.status == 'accepted':
                self.accepted_date = now()
                self.rejected_date = None
            elif self.status == 'rejected':
                self.rejected_date = now()
                self.accepted_date = None
            else:
                self.accepted_date = None
                self.rejected_date = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Application {self.application_id} - {self.status}"
    

    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.CharField(max_length=20, choices=[('light', 'Light Mode'), ('dark', 'Dark Mode')], default='light')
    font_size = models.CharField(max_length=10, choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')], default='medium',blank=True )
    contrast_mode = models.CharField(max_length=20, choices=[('default', 'Default'), ('high', 'High Contrast')], default='default',blank=True)

    def __str__(self):
        return self.user.username