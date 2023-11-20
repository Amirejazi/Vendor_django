from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, mobile_number, email=None, first_name="", last_name="", mobile_activate_code=None, email_activate_code=None, password=None):
        if not mobile_number:
            raise ValueError("شماره موبایل را وارد کنید!")

        user = self.model(
            mobile_number=mobile_number,
            first_name=first_name,
            last_name=last_name,
            mobile_activate_code=mobile_activate_code,
            email_activate_code=email_activate_code
        )
        if email:
            user.email = self.normalize_email(email),
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, first_name, last_name, email=None, password=None, mobile_activate_code=None):
        user = self.create_user(
            mobile_number=mobile_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            mobile_activate_code=mobile_activate_code,
            password=password
        )
        user.is_admin = True
        user.is_mobile_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

