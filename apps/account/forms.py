from django import forms
from django.core.exceptions import ValidationError
from apps.account.models import User
from apps.home.forms import FormWithCaptcha, ModelFormWithCaptcha


class UserRegisterForm(ModelFormWithCaptcha):
    #  (یادآوری) برای اینکه موبایل توسط فرم اعتبارسنچی نشود
    mobile_number = forms.CharField(required=True,
                                    error_messages={'required': 'شماره موبایل نمیتواند خالی باشد!'}
                                    ,widget=forms.TextInput({'data-val-required': 'شماره موبایل نمیتواند خالی باشد!', 'data-val': 'true'}))
    rePassword = forms.CharField(
        required=True,
        error_messages={'required': 'این فیلد نمیتواند خالی باشد!'},
        widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password']
        widgets = {
            'password': forms.PasswordInput(),
            'first_name': forms.TextInput(attrs={'data-val-required': 'این فیلد نمیتواند خالی باشد!', 'data-val': 'true'}),
            'last_name': forms.TextInput(attrs={'data-val-required': 'این فیلد نمیتواند خالی باشد!', 'data-val': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].error_messages.update({
            'required': 'این فیلد نمیتواند خالی باشد!',
        })

        self.fields['last_name'].error_messages.update({
            'required': 'این فیلد نمیتواند خالی باشد!',
        })
        self.fields['password'].error_messages.update({
            'required': 'این فیلد نمیتواند خالی باشد!',
        })

    def clean_rePassword(self):
        pass1 = self.cleaned_data["password"]
        pass2 = self.cleaned_data["rePassword"]
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError('رمز عبور با تکرار آن مغایرت دارد!')
        return pass2


class VerifyRegisterForm(forms.Form):
    active_code = forms.CharField(required=True, error_messages={'required': 'این فیلد نمیتواند خالی باشد!'}, widget=forms.TextInput())


class UserLoginForm(FormWithCaptcha):
    mobile_number = forms.CharField(required=True, error_messages={'required': 'این فیلد نمیتواند خالی باشد!'}, widget=forms.TextInput())
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class ForgotPasswordForm(FormWithCaptcha):
    mobile_number = forms.CharField(required=True, error_messages={'required': 'این فیلد نمیتواند خالی باشد!'}, widget=forms.TextInput())


class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True, error_messages={'required': 'رمز عبور نمیتواند خالی باشد!'}, widget=forms.PasswordInput())
    re_password = forms.CharField(required=True, error_messages={'required': 'تکراررمز عبور نمیتواند خالی باشد!'}, widget=forms.PasswordInput())

    def clean_re_password(self):
        pass1 = self.cleaned_data["password"]
        pass2 = self.cleaned_data["re_password"]
        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError('رمز عبور با تکرار آن مغایرت دارد!')
        return pass2