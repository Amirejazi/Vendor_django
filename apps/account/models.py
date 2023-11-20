import os
from enum import Enum
from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from .manager import CustomUserManager
from services.images_service import DeleteOldImageForSave, DeleteImage


def upload_user_image(instance, filename):
    filename, ext = os.path.splitext(filename)
    return f"uploads/user_avatar/{uuid4()}{ext}"


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='نام خانوادگی')
    mobile_number = models.CharField(max_length=200, unique=True, verbose_name='شماره موبایل')
    mobile_activate_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='کد فعال سازی موبایل')
    is_mobile_active = models.BooleanField(default=False, verbose_name='موبایل فعال / غیر فعال')
    email = models.EmailField(max_length=200, unique=True, blank=True, null=True, verbose_name='ایمیل')
    email_activate_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='کد فعال سازی موبایل')
    is_email_active = models.BooleanField(default=False, verbose_name='موبایل فعال / غیر فعال')
    image_name = models.ImageField(upload_to=upload_user_image, null=True, blank=True, verbose_name='آواتار')
    register_date = models.DateField(auto_now_add=True, verbose_name='تاریخ ثبت نام')
    is_admin = models.BooleanField(default=False, verbose_name='مدیر')
    is_superuser = models.BooleanField(default=False, verbose_name='مدیرکل')

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        if self.first_name == '' and self.last_name == '':
            return self.mobile_number
        else:
            return f"{self.first_name} {self.last_name}"

    def get_fullname(self):
        return self.first_name + ' ' + self.last_name

    @property
    def is_staff(self):
        return self.is_admin

    def save(self, *args, **kwargs):
        DeleteOldImageForSave(User, self, 'image_name')
        super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        DeleteImage(self, 'image_name')
        super().delete(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['register_date']),
            models.Index(fields=['mobile_number']),
        ]
        permissions = [
            ("admin-panel", "پنل مدیریت")
        ]
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        db_table = "t_users"


