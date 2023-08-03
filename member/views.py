import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)
from authentication.models import ActivationOTP, User
from userprofile.serializers import UserProfileSerializer
from rest_framework.permissions import IsAuthenticated
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from django.db import IntegrityError
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


class MemberAPIView(APIView):
    """
    API for handling Member CRUD.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Create a new member.

        Parameters:
        request (Request): The incoming request object.

        Returns:
        Response: JSON response containing the created member details.
                  Error response if the member creation fails.
        """
        serializer = UserProfileSerializer(
            data=request.data, context={"extra": request.data}
        )

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if serializer.is_valid():
            # Check if the requested user has parent_id
            if request.user.parent_id:
                return Response(
                    {
                        "message": _("You are not authorized to add members."),
                        "data": None,
                    },
                    status=HTTP_403_FORBIDDEN,
                    headers={"Content-Language": language_code},
                )

            # Generate a random 6-digit password
            password = "".join(random.choices("0123456789", k=6))

            try:
                # Create a new User
                user = User.objects.create_user(
                    username=request.data.get("mobile_number"),
                    password=password,
                    is_active=False,
                    first_name=request.data.get("first_name"),
                    last_name=request.data.get("last_name"),
                    parent_id=request.user,
                )
                # Generate OTP and save it to the database
                otp = 1234
                ActivationOTP.objects.create(user=user, otp=otp)

                # Assign the newly created User to the UserProfile
                serializer.validated_data["user"] = user

                serializer.save()

                return Response(
                    {
                        "message": _("Member created successfully."),
                        "data": serializer.data,
                    },
                    status=HTTP_201_CREATED,
                    headers={"Content-Language": language_code},
                )
            except IntegrityError:
                return Response(
                    {"message": _("Username already exists."), "data": None},
                    status=HTTP_400_BAD_REQUEST,
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
        Retrieve member(s) based on the provided parameters.

        Parameters:
        request (Request): The incoming request object.
        name (str, optional): The name to search for members.
        member_id (int, optional): The ID of a specific member to retrieve.

        Returns:
        Response: JSON response containing the member details.
                  Error response if the member(s) do not exist.
        """
        name = request.GET.get("name")
        member_id = request.GET.get("member_id")
        flag = request.GET.get("flag")

        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        if member_id:
            try:
                member = UserProfile.objects.get(id=member_id)
                serializer = UserProfileSerializer(member)
                return Response(
                    {
                        "message": _("Member retrieved successfully."),
                        "data": serializer.data,
                    },
                    status=HTTP_200_OK,
                    headers={"Content-Language": language_code},
                )
            except UserProfile.DoesNotExist:
                return Response(
                    {"message": _("Member not found."), "data": None},
                    status=HTTP_404_NOT_FOUND,
                    headers={"Content-Language": language_code},
                )

        if flag == "family_member":
            # Retrieve all family members
            queryset = UserProfile.objects.filter(user__parent_id=request.user)
        else:
            # Retrieve all members
            queryset = UserProfile.objects.all()

        if name:
            # Split the name into first name and last name
            names = name.split()
            first_name = names[0] if names else ""
            last_name = names[-1] if len(names) > 1 else ""

            if first_name and last_name:
                # Filter by exact match for both first name and last name
                queryset = queryset.filter(
                    Q(
                        user__first_name__iexact=first_name,
                        user__last_name__iexact=last_name,
                    )
                )
            else:
                # Filter by partial match on either first name or last name
                queryset = queryset.filter(
                    Q(user__first_name__icontains=name)
                    | Q(user__last_name__icontains=name)
                )
        # Order the queryset by created_at field in descending order
        queryset = queryset.order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = UserProfileSerializer(result_page, many=True)

        return paginator.get_paginated_response(
            {"message": _("Members retrieved successfully."), "data": serializer.data}
        )
