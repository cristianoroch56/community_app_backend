from django.urls import path
from news.views import ListNewsAPI, NewsSearchAPIView

urlpatterns = [
    # List News API
    path("", ListNewsAPI.as_view(), name="list_news"),
    path("<int:news_id>/", ListNewsAPI.as_view(), name="list_news"),
    path("search_news/", NewsSearchAPIView.as_view(), name="news_search"),
]
