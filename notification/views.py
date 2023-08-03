from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SendNotification
from notification.serializers import SendNotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from services.pagination import CustomPagination
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


class UserNotificationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        paginator = self.pagination_class()
        user = request.user
        if SendNotification.objects.filter(user=user).exists():
            notification_obj = SendNotification.objects.filter(user=user).order_by(
                "-created_at"
            )
            paginated_notification = paginator.paginate_queryset(
                notification_obj, request
            )
            serializer = SendNotificationSerializer(paginated_notification, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                {"message": _("No Notification arrived"), "data": None},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

    def patch(self, request, pk):
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if SendNotification.objects.filter(id=pk).exists():
            notification = SendNotification.objects.get(id=pk)
            notification.is_read = True
            notification.save()  
            return Response(
                {"message": _("Notification updated succeessfully"), "data": notification.is_read},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {"message": _("Notification not found")},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )

    def delete(self, request, pk):
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if SendNotification.objects.filter(id=pk).exists():
            notification = SendNotification.objects.get(id=pk)
            notification.delete()
            return Response(
                {"message": _("Notification deleted succeessfully"), "data": None},
                status=HTTP_200_OK,
                headers={"Content-Language": language_code},
            )
        else:
            return Response(
                {"message": _("Notification not found")},
                status=HTTP_400_BAD_REQUEST,
                headers={"Content-Language": language_code},
            )
