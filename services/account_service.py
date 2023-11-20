from random import randint
from uuid import uuid4
import requests
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from apps.account.models import User
from apps.account.enums import RegisterUserResult, LoginUserResult, ForgotPasswordResult, ActivateMobileResult, ChangePasswordResult


def SendVerificationSms(mobile_number, activate_code):
    api_key = "XZh5yNh3GgxU0vRh5wpk2VxUaulK5t9h2azem4xeEhw="
    pattern_id = "77uyjnndc7cyhwx"
    number_of_sender = "+9810004223"
    url = f"http://ippanel.com:8080/?apikey={api_key}&pid={pattern_id}&fnum={number_of_sender}&tnum={mobile_number}&p1=active_code&v1={activate_code}"
    requests.get(url)


def GenerateOTP():
    return randint(10000, 99999)


def StoreActiveCodeInCatch(user):
    # ذخیره کد برای 2 دقیقه و 15 ثانیه
    cache.set(f'otp_{user.id}', user.mobile_activate_code, 135)


def CheckActiveCode(user, entered_otp):
    stored_otp = cache.get(f'otp_{user.id}')
    if stored_otp:
        if str(stored_otp) == entered_otp:
            return ActivateMobileResult.Success
        else:
            return ActivateMobileResult.NotMatch
    else:
        return ActivateMobileResult.NotFound


def RegisterUser(user_register_form):
    data = user_register_form.cleaned_data
    try:
        user = User.objects.get(mobile_number=data['mobile_number'])
        if not user.is_mobile_active:
            user.mobile_activate_code = GenerateOTP()
            user.save()
            SendVerificationSms(user.mobile_number, user.mobile_activate_code)
            StoreActiveCodeInCatch(user)
            return RegisterUserResult.Success
        else:
            return RegisterUserResult.MobileExists
    except User.DoesNotExist:
        user = User.objects.create_user(
                first_name=data['first_name'],
                last_name=data['last_name'],
                mobile_number=data['mobile_number'],
                password=data['password'],
                mobile_activate_code=GenerateOTP(),
                email_activate_code=uuid4()
        )
        SendVerificationSms(user.mobile_number, user.mobile_activate_code)
        StoreActiveCodeInCatch(user)
        return RegisterUserResult.Success


def ResultLogin(user_login_form):
    data = user_login_form.cleaned_data
    try:
        user = User.objects.get(mobile_number=data['mobile_number'])
        if not user.is_mobile_active:
            return LoginUserResult.NotActivated
        if not check_password(data['password'], user.password):
            return LoginUserResult.NotFound
        return LoginUserResult.Success
    except User.DoesNotExist:
        return LoginUserResult.NotFound


def ForgotPasswordVerification(forgot_password_form):
    data = forgot_password_form.cleaned_data
    try:
        user = User.objects.get(mobile_number=data['mobile_number'])
        user.mobile_activate_code = randint(10000, 99999)
        user.save()
        SendVerificationSms(user.mobile_number, user.mobile_activate_code)
        StoreActiveCodeInCatch(user)
        return ForgotPasswordResult.Success
    except User.DoesNotExist:
        return ForgotPasswordResult.NotFound


def EditProfileUser(form, user):
    data = form.cleaned_data
    user_db = get_object_or_404(User, id=user.id)
    user_db.first_name = data['first_name']
    user_db.last_name = data['last_name']
    user_db.image_name = data['avatar']
    user_db.save()


def ChangeUserPassword(form, request):
    data = form.cleaned_data
    user = get_object_or_404(User, id=request.user.id)
    if check_password(data['current_password'], user.password):
        if data['current_password'] != data['new_password']:
            user.set_password(data['new_password'])
            user.save()
            return ChangePasswordResult.Success
        else:
            return ChangePasswordResult.CurrentPassIsNewCorrect
    else:
        return ChangePasswordResult.CurrentPassNotCorrect
