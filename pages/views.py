from rest_framework.views import APIView
from rest_framework.response import Response
from pages.models import Pages
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


class PagesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        slug = request.query_params.get("slug")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if Pages.objects.filter(slug=slug).exists():
            pages = Pages.objects.get(slug=slug)
            return Response(
                {"message": _("Retrieved successfully"), "data": pages.body},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {"message": _("Provide correct slug"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )
