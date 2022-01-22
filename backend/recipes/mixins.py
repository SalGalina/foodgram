from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets


class ListRetrieveModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class LikeRecipeMixin:

    def like(self, request, pk, serializer_class):
        data = {'owner': request.user.id, 'recipe': pk}
        context = {"request": request}
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data

    def unlike(self, request, pk, model_class):
        get_object_or_404(
            model_class,
            owner=request.user,
            recipe=pk
        ).delete()
