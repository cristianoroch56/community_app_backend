from django.urls import path
from member.views import MemberAPIView

urlpatterns = [
    path("create_member/", MemberAPIView.as_view(), name="create_member"),
    path("get_member/", MemberAPIView.as_view(), name="get_member"),
]
