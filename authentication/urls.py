from django.urls import path
from authentication.views import (
    RegistrationAPIView,
    VerifyActivationOTPAPIView,
    ResendActivationOTPAPIView,
    LoginAPIView,
    ForgotPasswordAPIView,
    VerifyOTPForgotPasswordAPIView,
    ResetPasswordAPIView
)

urlpatterns = [
    # Registration API endpoint
    path("registration/", RegistrationAPIView.as_view(), name="registration"),
    # Activation otp verify
    path(
        "verify_activation_otp/",
        VerifyActivationOTPAPIView.as_view(),
        name="verify_activation_otp",
    ),
    # Resend activation otp
    path(
        "resend_activation_otp/",
        ResendActivationOTPAPIView.as_view(),
        name="resend_activation_otp",
    ),

    path("login/", LoginAPIView.as_view(), name="login"),

    path("forgetpasswordotp/", ForgotPasswordAPIView.as_view(), name="forgetpasswordotp"),

    path("verify_forgetpassword_otp/", VerifyOTPForgotPasswordAPIView.as_view(),
         name="verify_forgetpassword_otp"),

    path("reset_password/", ResetPasswordAPIView.as_view(), name="reset_password")
]
