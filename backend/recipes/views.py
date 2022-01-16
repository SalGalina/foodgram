import io
import csv
from django.contrib.auth import get_user_model
from django.db.models import Sum, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (
    Ingredient, Tag, Recipe, RecipeIngredient, Favorite, Shopping)
from .serializers import (
    IngredientSerializer,
    RecipeSerializer, RecipeCreateSerializer,
    TagSerializer,
    FavoriteSerializer,
    ShoppingSerializer
)
from .paginations import RecipesPageNumberPagination
from users.permissions import (IsAuthorOrAdminOrReadOnly)

User = get_user_model()


class ListRetrieveModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    pass


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related(Prefetch('tags')).all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = RecipesPageNumberPagination

    def get_serializer_class(self):
        if self.request.method == 'list':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(
            data={'owner': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            recipe=get_object_or_404(Recipe, id=pk),
            owner=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        serializer = ShoppingSerializer(
            data={'owner': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            Shopping,
            recipe=get_object_or_404(Recipe, id=pk),
            owner=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        ingredients = list(RecipeIngredient.objects.filter(
            recipe__shoppings__owner=self.request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            sum_amount=Sum('amount')
        ))
        with io.StringIO() as out:
            csv_writer = csv.writer(
                out, delimiter=',', lineterminator=';', quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow([
                ' ', ' ', 'СПИСОК ПРОДУКТОВ для ', 'выбранных ', 'рецептов:'
            ])
            csv_writer.writerow(['-', '-', '-', '-', '-'])
            for num, ingredient in enumerate(ingredients, start=1):
                prod = ingredient['ingredient__name']+': '
                amount = ingredient['sum_amount']
                unit = ingredient['ingredient__measurement_unit']
                csv_writer.writerow([num, '. ', prod, amount, unit])
            contents = out.getvalue()
            # как ни старалась - я не смогла LibreOffice
            # заставить открыть этот файл корректно.
            # Он воспринимает его как одну строку.
        response = Response(contents, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shopping.csv"'
        return Response(status=status.HTTP_200_OK)
