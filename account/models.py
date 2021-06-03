from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
import requests
from datetime import datetime
from datetime import datetime, timedelta
from userDjango import settings
# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self,username,password=None,**extra_fields):
        if not username:
            raise ValueError("Username is required")
        if self.checkNumber(username)==False:
            raise ValueError("Username must be a phone number")
        user=self.model(
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username,password):
        user=self.create_user(
            username=username,
            password=password,
        )
        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

    def checkNumber(self,username):
        if (username.isnumeric() == False):
            return False
        if (username[0] == "8"):
            if (len(username) == 11):
                if (username[1] == "7"):
                    #print(username[1])
                    return True
        elif (username[0:2] == "+7"):
            if (len(username) == 12):
                if (username[2] == "7"):
                    return True
        return False

class Account(AbstractBaseUser):
    #email=models.EmailField(verbose_name="email",max_length=60,unique=True)
    username=models.CharField(max_length=30,unique=True)
    data_joined=models.DateTimeField(verbose_name='data_joined',default=datetime.now)
    name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)
    image1=models.ImageField(blank=False,null=True)
    image2 = models.ImageField(blank=False, null=True)
    image3=models.ImageField(blank=False,null=True)

    is_admin=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)


    USERNAME_FIELD='username'
    #REQUIRED_FIELDS = ['name','surname']
    objects=MyAccountManager()
    def __str__(self):
        user_type="USER"
        if(self.is_superuser):
            user_type="SUPERUSER"
        return user_type+" "+self.username
    def has_perm(self,perm,obj=None):
        return self.is_admin
    def has_module_perms(self,app_Label):
        return True


class Door(models.Model):
    #id = models.AutoField(primary_key=True)
    door_name=models.CharField(max_length=200,null=True)
    qr_string=models.CharField(max_length=200,null=True)
    is_open=models.BooleanField(default=False)

    def __str__(self):
        return  self.door_name

class Camera(models.Model):
    is_open=models.BooleanField(default=False)
    user_id=models.IntegerField(null=True)

    def __str__(self):
        return  str(self.id)+" Camera: "+str(self.is_open)+" ID: "+str(self.user_id)

class QR(models.Model):
    #id = models.AutoField(primary_key=True)
    user_id=models.CharField(max_length=10,null=True)
    qr_string=models.CharField(max_length=100,null=True)
    #door_id=models.IntegerField(null=True)
    date_created = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return  self.qr_string

class Inside(models.Model):
    user_id=models.IntegerField(null=True)
    entry_time=models.DateTimeField(default=datetime.now)
    exit_time=models.DateTimeField(auto_now_add=False,null=True)
    spent_time=models.CharField(max_length=100,null=True)
    door_id=models.IntegerField(null=True)
    door_id_exit = models.IntegerField(null=True)
    #images=files[]

    def __str__(self):
        return  str(self.user_id)+" "+str(self.entry_time)+" "+str(self.exit_time)

class ReturnedValueFromScript(models.Model):
    returned_value=models.IntegerField(null=True)

    def __str__(self):
        return  str(self.id)+" "+str(self.returned_value)

