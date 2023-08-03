from rest_framework.views import APIView
from news.models import News
from news.serializers import NewsSerializer
from rest_framework.permissions import IsAuthenticated
from services.pagination import CustomPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK
from django.utils.translation import gettext as _
from django.utils.translation import activate, get_language


# Create your views here.
class ListNewsAPI(APIView):
    # apply pagination and authentication in Get News
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        query = request.query_params.get("flag", "")
        paginator = self.pagination_class()

        # Display latest News first
        news = News.objects.order_by("-created_at")
        reported_news = News.objects.filter(is_reported=True).order_by("-created_at")
        if query == "reported_news":
            data = reported_news
        else:
            data = news
        paginated_news = paginator.paginate_queryset(data, request)
        serializer = NewsSerializer(paginated_news, many=True)
        return paginator.get_paginated_response(serializer.data)

    def patch(self, request, news_id):
        # Activate the language based on the request header
        activate(request.META.get("HTTP_ACCEPT_LANGUAGE"))
        # Get the current language code
        language_code = get_language()

        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            return Response(
                {"message": _("News not found"), "data": None},
                status=HTTP_404_NOT_FOUND,
                headers={"Content-Language": language_code},
            )

        news.is_reported = True
        news.save()
        serializer = NewsSerializer(news)
        return Response(
            {"message": _("News reported successfully"), "data": serializer.data},
            status=HTTP_200_OK,
            headers={"Content-Language": language_code},
        )


class NewsSearchAPIView(APIView):
    # apply pagination and authentication in Get News
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get(self, request):
        query = request.query_params.get("news", "")
        if query:
            # Perform search based on the query parameter
            results = News.objects.filter(news_title__icontains=query)
        else:
            # Return all news if no query is provided
            results = News.objects.all()

        paginator = self.pagination_class()

        paginated_news = paginator.paginate_queryset(results, request)
        serializer = NewsSerializer(paginated_news, many=True)
        return paginator.get_paginated_response(serializer.data)
