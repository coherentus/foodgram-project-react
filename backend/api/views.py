from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.viewsets import ReadOnlyModelViewSet

from logic.models import Basket, FavourRecipe, Follow
from recipes.models import Component, Product, Recipe, Tag
from users.models import CustomUser as User
from .filters import ProductSearchFilter, RecipeQueryParamFilter
from .paginations import PageLimitNumberPagination
from .permissions import AuthorOrReadOnly
from .serializers import (
    CustomUserSerializer, ProductSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscribeSerializer, TagSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    """Endpoint '/api/tags' view.

    Permissions: IsAuthenticatedOrReadOnly from global settings.
    Pagination: None.
    Model: recipes.Tag.
    Allowed http methods/action:
    GET -list   guest
    GET -detail guest
    Extra-endpoints: None.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None


class ProductViewSet(ReadOnlyModelViewSet):
    """Endpoint '/api/ingredients/' view.

    Permissions: IsAuthenticatedOrReadOnly from global settings.
    Pagination: None.
    Model: recipes.Product.
    Search field 'name'.
    Allowed http methods/action:
    GET -list       guest
    GET -detail     guest
    Extra-endpoints: None.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (ProductSearchFilter,)
    search_fields = ('^name',)
    http_method_names = ('get',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Endpoint '/api/recipes/' view.

    Permissions: AuthorOrReadOnly custom.
    Pagination: Yes.
    Filters: Yes.
    Model: recipes.Recipe.
    Filter fields: author, tags.slug, is_in_shoping_cart, is_favorited
    Allowed http methods/action:
    -list:      GET guest   POST auth-user
    -detail:    GET guest   PATH, DELETE auth-user
    Extra-endpoints allowed only auth-user:
    /api/recipes/{id}/shopping_cart/        methods:    get, delete
    /api/recipes/download_shopping_cart/    methods:    get
    /api/recipes/{id}/favorite/             methods:    get, delete
    """
    permission_classes = (AuthorOrReadOnly, )
    pagination_class = PageLimitNumberPagination
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeQueryParamFilter

    http_method_names = ('get', 'post', 'put', 'patch', 'delete', )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        else:
            return RecipeWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        # headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED,  # headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )

    def add_recipe(self, request, model, pk=None):
        """Add recipe into favorites or basket of current user.

        Before add need check obj exist and exist in db.
        """
        user = request.user
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Ошибка. Попытка повторного добавления рецепта.'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeReadSerializer(recipe, fields='__all__')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_recipe(self, request, model, pk=None):
        """Delete recipe from favorites or basket of current user.

        Before delete need check obj exist and exist in db.
        """
        user = request.user
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Ошибка. Попытка удаления несуществующего рецепта.'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart', url_name='basket',
        # serializer_class=RecipeShowSerializer
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'DELETE':
            return self.del_recipe(request, Basket, pk)
        elif request.method == 'POST':
            return self.add_recipe(request, Basket, pk)
        return None

    @action(
        detail=True, methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='favorite', url_name='favorite',
    )
    def add_del_favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_recipe(request, FavourRecipe, pk)
        elif request.method == 'DELETE':
            return self.del_recipe(request, FavourRecipe, pk)
        return None

    @action(
        detail=False, methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart', url_name='txt_basket',
    )
    def download_text_file(self, request):
        """Make and response txt-file from current user's basket."""
        user = request.user
        if not user.basket.exists():
            return Response({
                'errors': 'Ошибка. Попытка получения пустого списка покупок.'
            }, status=status.HTTP_400_BAD_REQUEST)

        basket_components = Component.objects.filter(
            recipe__basket_recipes__user=user
        ).values(
            'product__name',
            'product__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('product__name')

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        response.write('Список продуктов к покупке\r\n\r\n')
        for component in basket_components:
            response.write(
                f'* {component["product__name"]} - '
                f'{component["amount"]} '
                f'{component["product__measurement_unit"]} \r\n'
            )
        return response


class CustomUserViewSet(UserViewSet):
    """Endpoint '/api/users/' view.

    Permissions: depending on the point. Global or custom.
    Pagination: depending on the point.
    Models: depending on the point: users.CustomUser, logic.Follow,
                                    recipes.Recipe
    Allowed http methods/action:
    Extra-endpoints:
    url_path                    methods         url_name
    /api/users/subscriptions/   GET  -list      'subscriptions' auth-user
    need pagination
    /api/users/{id}/subscribe/  POST  -detail    'make_subscribe' auth-user
    need check self-follow, exist-follow
    /api/users/{id}/subscribe/  DELETE -detail  'del_subscribe' auth-user
    need check exist-follow
    """
    queryset = User.objects.all().prefetch_related('recipes')
    serializer_class = CustomUserSerializer
    pagination_class = PageLimitNumberPagination
    http_method_names = ('get', 'post', 'delete')
    lookup_field = 'pk'
    lookup_value_regex = '[0-9]'

    @action(
        detail=False, methods=('get', ),
        url_path='subscriptions', url_name='subscriptions',
        permission_classes=(IsAuthenticated, ),
        serializer_class=SubscribeSerializer
    )
    def get_subscriptions(self, request):
        """Get and return current user's subscriptions."""
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=('post', 'delete'),
        url_path='subscribe',
        url_name='make_subscribe',
        permission_classes=(IsAuthenticated, ),
        serializer_class=SubscribeSerializer,
    )
    def add_del_sibscription(self, request, pk=None):
        """Create or delete subscription from current user to author."""
        if request.method == 'POST':
            return self.add_follow(request, pk)
        elif request.method == 'DELETE':
            return self.del_follow(request, pk)
        return None

    def add_follow(self, request, pk=None):
        """Create subscription from current user to author.

        Before add need check obj exist and exist in subscriptions.
        """
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if user == author:
            return Response({
                'errors': 'Ошибка. Попытка подписки на себя.'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow, _ = Follow.objects.get_or_create(user=user, author=author)
        if _:
            serializer = SubscribeSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({
            'errors': 'Ошибка. Попытка повторной подписки на автора.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def del_follow(self, request, pk=None):
        """Delete subscription from current user to author.

        Before delete need check obj exist and exist in subscriptions.
        """
        user = request.user
        author = get_object_or_404(User, pk=pk)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
