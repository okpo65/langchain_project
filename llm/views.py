from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class GetMRCResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        return Response({'result': ''}, status=status.HTTP_200_OK)


class GetQAResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        return Response({'result': ''}, status=status.HTTP_200_OK)


class PollForResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        return Response({'result': ''}, status=status.HTTP_200_OK)
