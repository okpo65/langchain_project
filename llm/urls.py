from django.urls import path
from rest_framework import routers

import llm.views

router = routers.SimpleRouter(trailing_slash=False)

urlpatterns = [
    path('chat/mrc', llm.views.RequestMRCAPIView.as_view()),
    path('chat/qa', llm.views.RequestQAAPIView.as_view()),
    path('chat/state', llm.views.PollForResultAPIView.as_view()),
    path('chat/result', llm.views.GetResultLLMLog.as_view()),
    path('create/session', llm.views.CreateSessionAPIView.as_view())

] + router.urls