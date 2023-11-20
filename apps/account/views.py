from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from apps.account.forms import UserRegisterForm, UserLoginForm, ForgotPasswordForm, VerifyRegisterForm, ChangePasswordForm
from apps.account.enums import RegisterUserResult, LoginUserResult, ForgotPasswordResult, ActivateMobileResult
from apps.account.models import User
from services.account_service import RegisterUser, ResultLogin, ForgotPasswordVerification, CheckActiveCode, GenerateOTP, StoreActiveCodeInCatch, \
    SendVerificationSms


class RegisterUserView(View):
    template_name = 'account_app/register_user.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home:Index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            res = RegisterUser(form)
            if res is RegisterUserResult.MobileExists:
                form.add_error('mobile_number', 'تلفن همراه وارد شده تکراری میباشد!')
                messages.error(request, 'تلفن همراه وارد شده تکراری می باشد!')
                return render(request, self.template_name, {'form': form})
            else:
                request.session['mobile_number'] = form.cleaned_data['mobile_number']
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد:)')
                messages.info(request, 'کد تایید تلفن همراه برای شما ارسال شد')
                return redirect('Account:VerifyRegister')
        if form.errors.get('captcha', ''):
            messages.error(request, 'کپچای شما تایید نشد!')
        return render(request, self.template_name, {'form': form})

## ===========================================================================================================================================


class VerifyRegister(View):
    template_name = 'account_app/verify_active_code.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home:Index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = VerifyRegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = VerifyRegisterForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['active_code']
            mobile_number = request.session['mobile_number']
            user = get_object_or_404(User, mobile_number=mobile_number)
            res = CheckActiveCode(user, entered_otp)
            if res is ActivateMobileResult.NotFound:
                messages.warning(request, 'زمان استفاده از کد تایید تمام شده است لطفا برای دریافت کد جدید اقدام کنید')
                return render(request, self.template_name, {'form': form})
            elif res is ActivateMobileResult.NotMatch:
                messages.error(request, 'کد تایید وارد شده نادرست است')
                return render(request, self.template_name, {'form': form})
            elif res is ActivateMobileResult.Success:
                user.is_mobile_active = True
                user.mobile_activate_code = GenerateOTP()
                user.save()
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد :)')
                return redirect('Home:Index')
        return render(request, self.template_name, {'form': form})

## ===========================================================================================================================================


def SendAgainOTP(request):
    mobile_number = request.session['mobile_number']
    user = get_object_or_404(User, mobile_number=mobile_number)
    user.mobile_activate_code = GenerateOTP()
    user.save()
    SendVerificationSms(user.mobile_number, user.mobile_activate_code)
    StoreActiveCodeInCatch(user)
    if request.GET.get('forgot-pass'):
        return redirect('Account:VerifyMobileForgotPass')
    return redirect('Account:VerifyRegister')

## ===========================================================================================================================================


class LoginUserView(View):
    template_name = 'account_app/login_user.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home:Index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            result = ResultLogin(form)
            if result is LoginUserResult.NotFound:
                messages.error(request, 'اطلاعات وارد شده اشتباه می باشد!')
                return render(request, self.template_name, {'form': form})
            if result is LoginUserResult.NotActivated:
                messages.warning(request, 'حساب کاربری شما فعال نمی باشد!')
                return render(request, self.template_name, {'form': form})
            if result is LoginUserResult.Success:
                user = User.objects.get(mobile_number=form.cleaned_data['mobile_number'])
                login(request, user)
                messages.success(request, 'ورود شما با موفقیت انجام شد:)')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
        if form.errors.get('captcha', ''):
            messages.error(request, 'کپچای شما تایید نشد!')
            return render(request, self.template_name, {'form': form})
        messages.error(request, 'اطلاعات وارد شده نا معتبر می باشد!', 'danger')
        return render(request, self.template_name, {'form': form})

## ===========================================================================================================================================


class LogoutUserView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('Home:Index')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('Home:Index')

## ===========================================================================================================================================


class ForgotPassword(View):
    def get(self, request, *args, **kwargs):
        form = ForgotPasswordForm()
        return render(request, 'account_app/forgot_password.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            res = ForgotPasswordVerification(form)
            if res is ForgotPasswordResult.NotFound:
                messages.error(request, 'موبایل وارد شده اشتباه می باشد!')
                return render(request, 'account_app/forgot_password.html', {'form': form})
            else:
                request.session['mobile_number'] = form.cleaned_data['mobile_number']
                messages.info(request, 'کد تایید تلفن همراه برای شما ارسال شد')
                return redirect('Account:VerifyMobileForgotPass')
        if form.errors.get('captcha', ''):
            messages.error(request, 'کپچای شما تایید نشد!')
        return render(request, 'account_app/forgot_password.html', {'form': form})

## ===========================================================================================================================================


class VerifyMobileForgotPass(View):
    template_name = 'account_app/verify_active_code.html'

    def get(self, request, *args, **kwargs):
        form = VerifyRegisterForm()
        context = {
            'form': form,
            'forgot_pass': True
        }
        return render(request, 'account_app/verify_active_code.html', context)

    def post(self, request, *args, **kwargs):
        form = VerifyRegisterForm(request.POST)
        context = {
            'form': form,
            'forgot_pass': True
        }
        if form.is_valid():
            entered_otp = form.cleaned_data['active_code']
            mobile_number = request.session['mobile_number']
            user = get_object_or_404(User, mobile_number=mobile_number)
            res = CheckActiveCode(user, entered_otp)
            if res is ActivateMobileResult.NotFound:
                messages.warning(request, 'زمان استفاده از کد تایید تمام شده است لطفا برای دریافت کد جدید اقدام کنید')
                return render(request, self.template_name, context)
            elif res is ActivateMobileResult.NotMatch:
                messages.error(request, 'کد تایید وارد شده نادرست است')
                return render(request, self.template_name, context)
            elif res is ActivateMobileResult.Success:
                return redirect('Account:ChangPassword')
        return render(request, self.template_name, context)

## ===========================================================================================================================================


class ChangPasswordView(View):
    template_name = 'account_app/change_password.html'

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            mobile_number = request.session['mobile_number']
            user = get_object_or_404(User, mobile_number=mobile_number)
            user.set_password(data['password'])
            user.active_code = GenerateOTP()
            user.save()
            messages.success(request, 'رمز عبور با موفقیت تغییر کرد :)')
            return redirect('Account:Login')
        else:
            return render(request, self.template_name, {'form': form})
