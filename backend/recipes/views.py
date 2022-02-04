import csv
import io

from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsAuthorOrAdminOrReadOnly

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import LikeRecipeMixin, ListRetrieveModelViewSet
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, Shopping,
                     Tag)
from .paginations import RecipesPageNumberPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(LikeRecipeMixin, viewsets.ModelViewSet):
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
        data = self.like(request, pk, FavoriteSerializer)
        return Response(data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        self.unlike(request, pk, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        data = self.like(request, pk, ShoppingSerializer)
        return Response(data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        self.unlike(request, pk, Shopping)
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
                out, delimiter=',', lineterminator='\n',
                quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow([
                ' ', ' ', 'СПИСОК ПРОДУКТОВ для ', 'выбранных ', 'рецептов:'
            ])
            csv_writer.writerow(['-', '-', '-', '-', '-'])
            for num, ingredient in enumerate(ingredients, start=1):
                prod = ingredient['ingredient__name'] + ': '
                amount = ingredient['sum_amount']
                unit = ingredient['ingredient__measurement_unit']
                csv_writer.writerow([num, '. ', prod, amount, unit])
            contents = out.getvalue()
        response = Response(contents,
                            content_type='text/csv',
                            status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename="shopping.csv"'

        return response
