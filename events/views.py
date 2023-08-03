from rest_framework.views import APIView
from events.models import Events
from events.serializers import EventSerializers
from rest_framework.permissions import IsAuthenticated
from services.pagination import CustomPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language
from django.utils import timezone


class ListEventsAPI(APIView):
    # apply pagination and authentication in Get Events
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        paginator = self.pagination_class()

        # Display latest Events first
        now = timezone.now()
        events = Events.objects.filter(event_date__lte=now).order_by(
            "-event_date"
        )
        paginated_events = paginator.paginate_queryset(events, request)
        serializer = EventSerializers(
            paginated_events, many=True, context={"user": request.user.id}
        )

        # Filter and include upcoming events
        upcoming_events = Events.objects.filter(event_date__gt=now).order_by(
            "event_date"
        )
        upcoming_serializer = EventSerializers(
            upcoming_events, many=True, context={"user": request.user.id}
        )

        # Get counts for both latest events and upcoming events
        latest_events_count = Events.objects.filter(event_date__lte=now).count()
        upcoming_events_count = Events.objects.filter(event_date__gt=now).count()

        return paginator.get_paginated_response(
            {
                "latest_events_count": latest_events_count,
                "upcoming_events_count": upcoming_events_count,
                "latest_events": serializer.data,
                "upcoming_events": upcoming_serializer.data,
            }
        )

    def patch(self, request, event_id):
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        try:
            event = Events.objects.get(id=event_id)
        except Events.DoesNotExist:
            return Response(
                {"message": _("Event not found"), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )
        user = request.user
        is_liked = request.data.get("is_liked")
        is_bookmarked = request.data.get("is_bookmarked")

        if is_liked:
            event.liked_by.add(user)
        else:
            event.liked_by.remove(user)

        if is_bookmarked:
            event.bookmarked_by.add(user)
        else:
            event.bookmarked_by.remove(user)

        event.save()

        serializer = EventSerializers(event, context={"user": request.user.id})
        return Response(
            {"message": _("Event updated successfully"), "data": serializer.data},
            status=HTTP_200_OK,
            headers={"Content-Language": language_code},
        )


class EventsSearchAPIView(APIView):
    # apply pagination and authentication in Get News
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        query = request.query_params.get("event", "")
        if query:
            # Perform search based on the query parameter
            results = Events.objects.filter(event_name__icontains=query)
        else:
            # Return all events if no query is provided
            results = Events.objects.all()

        paginator = self.pagination_class()

        paginated_news = paginator.paginate_queryset(results, request)
        serializer = EventSerializers(paginated_news, many=True)
        return paginator.get_paginated_response(serializer.data)
