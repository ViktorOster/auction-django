from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from blog.models import Post
from blog.serializers import postSerializer

class postList(APIView):

    def get(self, request):
        posts = Post.objects.all()
        serializer = postSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self):
        pass

class postSearch(APIView):

    def get(self, request, field_name):

        posts = Post.objects.filter(title__icontains=field_name).all()

        serializer = postSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self):
        pass
