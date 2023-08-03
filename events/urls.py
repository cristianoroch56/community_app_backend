from django.urls import path
from events.views import ListEventsAPI, EventsSearchAPIView

urlpatterns = [
    # List Events API
    path("", ListEventsAPI.as_view(), name="list_events"),
    path("<int:event_id>/", ListEventsAPI.as_view(), name="list_events"),
    path("search_events/", EventsSearchAPIView.as_view(), name="search_events"),
]
