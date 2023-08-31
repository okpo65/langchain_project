from django.urls import path
from rest_framework import routers

import llm.views

router = routers.SimpleRouter(trailing_slash=False)

urlpatterns = [
    path('chat/mrc', llm.views.GetMRCResultAPIView.as_view()),
    path('chat/qa', llm.views.GetQAResultAPIView.as_view()),
] + router.urls