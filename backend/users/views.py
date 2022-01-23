from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.paginations import RecipesPageNumberPagination

from .models import Subscribe
from .serializers import SubscribeListSerializer, SubscribeSerializer

User = get_user_model()


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        get_object_or_404(
            Subscribe,
            user=request.user,
            author=get_object_or_404(User, id=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListView(ListAPIView):
    pagination_class = RecipesPageNumberPagination
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        serializer = SubscribeListSerializer(
            self.paginate_queryset(
                User.objects.filter(subscribing__user=request.user)),
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)
