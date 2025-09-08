from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from accounts.models import *
from django.shortcuts import get_list_or_404
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import json
from rest_framework import permissions
# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data 
        data["message"] = "Login Successful"
        return Response(data, status=status.HTTP_200_OK)