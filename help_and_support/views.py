from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from help_and_support.models import HelpAndSupport
from help_and_support.serializers import HelpAndSupportSerializer
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


class HelpAndSupportAPIView(APIView):
    """
    API for handling Help and Support requests.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new help and support request.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the created request details.
                  Error response if the creation fails.
        """
        request.data["user"] = request.user.id
        serializer = HelpAndSupportSerializer(data=request.data)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("Help and support request created successfully."),
                    "data": serializer.data,
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

    def get(self, request):
        """
        Retrieve unsolved help and support requests.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the unsolved request details.
                Error response if the unsolved requests do not exist.
        """
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        try:
            requests = HelpAndSupport.objects.filter(status=False)
            serializer = HelpAndSupportSerializer(requests, many=True)
            return Response(
                {
                    "message": _(
                        "Unsolved help and support requests retrieved successfully."
                    ),
                    "data": serializer.data,
                },
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        except HelpAndSupport.DoesNotExist:
            return Response(
                {
                    "message": _("No help and support requests found."),
                    "data": None,
                },
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )
