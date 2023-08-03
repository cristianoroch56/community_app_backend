from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)
from message.models import Thread
from message.serializers import ThreadSerializer, MessageSerializer
from rest_framework.pagination import PageNumberPagination
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from django.db.models import Q


class ThreadsAPIView(APIView):
    """
    API view for listing and creating threads.
    Requires authentication using TokenAuthentication.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all threads.

        Returns:
            A response containing the list of threads.
        """
        user = request.user

        # Get the name parameter from the query string
        name = request.GET.get("name")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        threads = Thread.objects.filter(user1=user) | Thread.objects.filter(user2=user)
        if name:
            # Split the name into first name and last name
            names = name.split()
            first_name = names[0] if names else ""
            last_name = names[-1] if len(names) > 1 else ""

            if first_name and last_name:
                # Filter by exact match for both first name and last name
                threads = threads.filter(
                    Q(
                        user1__first_name__iexact=first_name,
                        user1__last_name__iexact=last_name,
                    )
                    | Q(
                        user2__first_name__iexact=first_name,
                        user2__last_name__iexact=last_name,
                    )
                )
            else:
                # Filter by partial match on either first name or last name
                threads = threads.filter(
                    Q(user1__first_name__icontains=name)
                    | Q(user1__last_name__icontains=name)
                    | Q(user2__first_name__icontains=name)
                    | Q(user2__last_name__icontains=name)
                )

            # Return none if the name matches the user's first name and last name
            if (
                user.first_name.lower() == first_name.lower()
                and user.last_name.lower() == last_name.lower()
            ):
                threads = None

        serializer = ThreadSerializer(threads, many=True)
        return Response(
            {"message": _("Threads retrieved successfully"), "data": serializer.data},
            status=HTTP_200_OK,
            headers={"Content-Language": language_code},
        )

    def post(self, request):
        """
        Create a new thread.

        Args:
            request: The HTTP request object containing the thread data.

        Returns:
            A response containing the created thread data if successful,
            or the validation errors if the data is not valid.
        """
        request.data["user1"] = request.user.id
        serializer = ThreadSerializer(data=request.data)

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": _("Thread created successfully"),
                    "data": serializer.data,
                },
                status=HTTP_201_CREATED,
                headers={"Content-Language": language_code},
            )
        return Response(
            {"message": serializer.errors, "data": None},
            status=HTTP_400_BAD_REQUEST,
            headers={"Content-Language": language_code},
        )


class MessagesAPIView(APIView):
    """
    API view for fetching messages.
    Requires authentication using TokenAuthentication.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all messages from a specific thread.

        Args:
            request: The HTTP request object.

        Returns:
            A paginated response containing the list of messages in the thread.
        """
        thread_id = request.query_params.get("thread_id")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        try:
            thread = Thread.objects.get(id=thread_id)
            messages = thread.chat_messages.order_by("-created_at")

            paginator = PageNumberPagination()
            paginator.page_size = 20
            paginated_messages = paginator.paginate_queryset(messages, request)

            serializer = MessageSerializer(paginated_messages, many=True)
            return paginator.get_paginated_response(
                {
                    "message": _("Messages retrieved successfully"),
                    "data": serializer.data,
                }
            )
        except Thread.DoesNotExist:
            return Response(
                {"message": _("Thread not found"), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )
