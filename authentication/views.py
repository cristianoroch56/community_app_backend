from authentication.models import ActivationOTP
from authentication.serializers import (
    ActivationOTPSerializer,
    UserSerializer,
    UserLoginSerializer,
    ResetPasswordSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_202_ACCEPTED,
    HTTP_401_UNAUTHORIZED,
)
from authentication.models import User
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from rest_framework.authtoken.models import Token
from authentication.models import ForgetPasswordOtp, ForgetPasswordToken
from userprofile.models import UserProfile
from fcm_django.models import FCMDevice


class RegistrationAPIView(APIView):
    """
    API View to register a new user.
    """

    def post(self, request):
        """
        Create a new user account by accepting user details

        Parameters:
        request (Request): The incoming request object

        Returns:
        Response: JSON response containing the user's details.
                  Error response if request is invalid or
                  user with the same username already exists
                  here also send the user profile id.
        """
        serializer = UserSerializer(data=request.data)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP and save to the database
            otp = 1234
            ActivationOTP.objects.create(user=user, otp=otp)
            # Create the UserProfile and save first_name and last_name there
            user_profile = UserProfile.objects.create(user=user)

            # TODO : Send otp to mobile number

            return Response(
                {
                    "message": _("User registered successfully."),
                    "data": None,
                },
                status=HTTP_201_CREATED,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {"message": serializer.errors, "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )


class VerifyActivationOTPAPIView(APIView):
    """
    API View to verify activation OTP.
    """

    def post(self, request):
        """
        Verify activation OTP for the user.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the verification
                  Error response if request is invalid or
                  OTP is incorrect.
        """
        serializer = ActivationOTPSerializer(data=request.data)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            return Response(
                {"message": _("OTP verified successfully."), "data": None},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {
                    "message": serializer.errors,
                    "data": None,
                },
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )


class ResendActivationOTPAPIView(APIView):
    """
    API View to resend activation OTP.
    """

    def post(self, request):
        """
        Resend the activation OTP to the user.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the status of the resend operation.
                  Error response if the user does not exist or is already activated.
        """
        username = request.data.get("username")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"message": _("User not found."), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )

        if user.is_active:
            return Response(
                {"message": _("User is already activated."), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

        activation_otp = ActivationOTP.objects.get(user=user)
        activation_otp.otp = 1234  # Generate a new OTP
        activation_otp.expires_at = timezone.now() + timezone.timedelta(
            minutes=5
        )  # Update expiration time
        activation_otp.save()

        # TODO: Resend the OTP to the user's mobile number

        return Response(
            {"message": _("Activation OTP resent successfully."), "data": None},
            status=HTTP_200_OK,
            headers={
                "Content-Language": language_code
            },  # Include the language code in the response headers
        )


class LoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        # If Serializer is valid then check validation
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            user_serializer = UserSerializer(user)
            
            # Deleting any previous stored token
            Token.objects.filter(user=user).delete()

            if "fcm_token" in request.data:
                # Set FCM token for user
                fcm_device = FCMDevice()
                fcm_device.registration_id = request.data["fcm_token"]
                fcm_device.type = request.data["device_type"]
                fcm_device.user = user
                fcm_device.save()

            # Token is created or get while user login
            token = Token.objects.create(user=user)
            return Response(
                {
                    "message": _("Login is Successful"),
                    "data": {"token": token.key, "user_details": user_serializer.data},
                },
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {
                    "message": serializer.errors,
                    "data": None,
                },
                status=HTTP_401_UNAUTHORIZED,
                headers={"Content-Language": language_code},
            )


class ForgotPasswordAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        # If user does not provide Phone number
        if username is None:
            return Response(
                {"message": _("Provide Phone number to send OTP"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

        # check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            otp = 1234
            ForgetPasswordOtp.objects.update_or_create(user=user, otp=otp)
            return Response(
                {"message": _("Forgot Password OTP successfully sent"), "data": None},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {
                    "message": _("Provide correct Phone number to send OTP"),
                    "data": None,
                },
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )


class VerifyOTPForgotPasswordAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        otp = request.data.get("otp")

        # Check if OTP is present in the request data
        if not otp:
            return Response(
                {"message": _("Provide OTP"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        # Check if OTP exists for the user
        try:
            forget_password_otp = ForgetPasswordOtp.objects.get(
                user__username=username, otp=otp
            )
        except ForgetPasswordOtp.DoesNotExist:
            return Response(
                {"message": _("Invalid OTP"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

        # Check if OTP has expired
        if forget_password_otp.expires_at < timezone.now():
            forget_password_otp.delete()
            return Response(
                {"message": _("OTP has expired"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

        user = User.objects.get(username=username)

        # Generate a new forget password token
        token, created = ForgetPasswordToken.objects.get_or_create(user=user)

        forget_password_otp.delete()

        return Response(
            {"message": _("OTP Verified Successfully"), "data": {"token": token.token}},
            status=HTTP_200_OK,
            headers={"Content-Language": language_code},
        )


class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"request": request}
        )

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            token_obj = ForgetPasswordToken.objects.get(user=user)
            token_obj.delete()

            return Response(
                {"message": _("Password reset successfully"), "data": None},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {"message": serializer.errors, "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )
