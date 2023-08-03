from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


class UserProfileAPIView(APIView):
    """
    API View for managing user profiles.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_profile(self, user):
        try:
            user_profile = UserProfile.objects.get(user=user)
            return user_profile
        except UserProfile.DoesNotExist:
            return None

    def put(self, request):
        """
        Update an existing user profile.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the updated user profile.
                  Error response if the user profile does not exist or
                  the request data is invalid.
        """
        user_profile = self.get_user_profile(request.user)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if user_profile is None:
            return Response(
                {"message": _("User profile not found."), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )

        serializer = UserProfileSerializer(
            user_profile, data=request.data, context={"extra": request.data}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("User profile is updated successfully."),
                    "data": serializer.data,
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
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

    def get(self, request):
        """
        Retrieve the details of a user profile.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the user profile details.
                  Error response if the user profile does not exist.
        """
        user_profile = self.get_user_profile(request.user)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if user_profile is None:
            return Response(
                {"message": _("User profile not found."), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )

        serializer = UserProfileSerializer(user_profile)
        serializer_data = serializer.data
        serializer_data["country_code"] = user_profile.user.country_code
        serializer_data["country_flag"] = user_profile.user.country_flag
        return Response(
            {
                "message": _("User profile retrieved successfully."),
                "data": serializer_data,
            },
            status=HTTP_200_OK,
            headers={"Content-Language": language_code},
        )

    def patch(self, request):
        """
        Update an existing user profile.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response indicating whether the update was successful or not.
        """
        user_profile = self.get_user_profile(request.user)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if user_profile is None:
            return Response(
                {"message": _("User profile not found."), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )

        # Toggle the push notification
        user_profile.push_notification = not user_profile.push_notification

        try:
            user_profile.save()
            return Response(
                {"message": _("Push notification is set."), "data": None},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        except:
            return Response(
                {
                    "message": _("Error occurred while updating the profile."),
                    "data": None,
                },
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                headers={"Content-Language": language_code},
            )
