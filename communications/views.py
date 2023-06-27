from django.shortcuts import render
from .models import NewsLetter
from .serializers import NewsLetterSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import mixins

# Create your views here.


class AddEmail(APIView):
    serializer_class = NewsLetterSerializer

    def post(self, request):
        # Check if request is from https://cranom.cloud
        if request.META.get('HTTP_ORIGIN') != 'https://cranom.cloud':
            return Response(
                {'message': 'Unauthorized'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        email = request.data.get('email')
        if NewsLetter.objects.filter(email=email).exists():
            return Response(
                {'message': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NewsLetterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
