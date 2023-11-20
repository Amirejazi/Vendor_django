from django.urls import path
from .views import RegisterUserView, LoginUserView, LogoutUserView, ForgotPassword, VerifyRegister, SendAgainOTP, VerifyMobileForgotPass, ChangPasswordView

app_name = 'Account'
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='Register'),
    path('verify-register/', VerifyRegister.as_view(), name='VerifyRegister'),
    path('send-otp/', SendAgainOTP, name='SendAgainOTP'),
    path('login/', LoginUserView.as_view(), name='Login'),
    path('logout/', LogoutUserView.as_view(), name='Logout'),
    path('forgot-pass/', ForgotPassword.as_view(), name='ForgotPassword'),
    path('verify-forgot-pass/', VerifyMobileForgotPass.as_view(), name='VerifyMobileForgotPass'),
    path('change-password/', ChangPasswordView.as_view(), name='ChangPassword'),
]
