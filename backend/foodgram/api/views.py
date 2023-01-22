from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import Exists, OuterRef, Value
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet
from posts.models import (Followers, Ingredient, Recipe,
                          Recipies_Ingredients, Tag)
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from users.models import User

from .filters import IngredientFilter
from .mixins import PermissionAndPaginationMixin
from .pangination import LimitPage
from .serializers import (FollowersSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          SubscribeRecipeSerializer, TagSerializer,
                          TokenSerializer, UserCreateSerializer,
                          UserListSerializer, UserPasswordSerializer)


IN_CART = ('1', 'true',)
NOT_IN_CART = ('0', 'false',)
DATE_FORMAT = '%d-%m-%Y %H:%M'


class RecipesViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    # filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPage

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    # def get_queryset(self):
    #     return Recipe.objects.annotate(
    #         is_favorited=Exists(
    #             Favorite_Recipe.objects.filter(
    #                 user=self.request.user, recipe=OuterRef('id'))),
    #         is_in_shopping_cart=Exists(
    #             Shopping.objects.filter(
    #                 user=self.request.user,
    #                 recipe=OuterRef('id')))
    #     ).select_related('author').prefetch_related(
    #         'tags', 'ingredients', 'recipe',
    #         'shopping_cart', 'favorite_recipe'
    #     ) if self.request.user.is_authenticated else Recipe.objects.annotate(
    #         is_in_shopping_cart=Value(False),
    #         is_favorited=Value(False),
    #     ).select_related('author').prefetch_related(
    #         'tags', 'ingredients', 'recipe',
    #         'shopping_cart', 'favorite_recipe')

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса."""
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset
        is_in_shopping = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping in IN_CART:
            queryset = queryset.filter(shopping_cart=user.id)
        elif is_in_shopping in NOT_IN_CART:
            queryset = queryset.exclude(shopping_cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in IN_CART:
            queryset = queryset.filter(favorite_recipe=user.id)
        if is_favorited in NOT_IN_CART:
            queryset = queryset.exclude(favorite_recipe=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def download_shopping_cart(self, request):
    #     """Качаем список с ингредиентами."""

    #     # @action(
    #     detail=False,
    #     methods=['get'],
    #     permission_classes=(IsAuthenticated,))   buffer = io.BytesIO()
    #     page = canvas.Canvas(buffer)
    #     pdfmetrics.registerFont(TTFont('tahoma','tahoma.TTF'))
    #     x_position, y_position = 50, 800
    #     shopping_cart = (
    #         request.user.shopping_cart.recipe.
    #         values(
    #             'ingredients__name',
    #             'ingredients__measurement_unit'
    #         ).annotate(amount=Sum('recipe__amount')).order_by())
    #     page.setFont('tahoma', 14)
    #     if shopping_cart:
    #         indent = 20
    #         page.drawString(x_position, y_position, 'Cписок покупок:')
    #         for index, recipe in enumerate(shopping_cart, start=1):
    #             page.drawString(
    #                 x_position, y_position - indent,
    #                 f'{index}. {recipe["ingredients__name"]} - '
    #                 f'{recipe["amount"]} '
    #                 f'{recipe["ingredients__measurement_unit"]}.')
    #             y_position -= 15
    #             if y_position <= 50:
    #                 page.showPage()
    #                 y_position = 800
    #         page.save()
    #         buffer.seek(0)
    #         return FileResponse(
    #             buffer, as_attachment=True, filename=SHOP)
    #     page.setFont('tahoma', 24)
    #     page.drawString(
    #         x_position,
    #         y_position,
    #         'Cписок покупок пуст!')
    #     page.save()
    #     buffer.seek(0)
    #     return FileResponse(buffer, as_attachment=True, filename=SHOP)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""

        if not request.user.shopping_cart.recipe.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredient = Recipies_Ingredients.objects.filter(
            recipe__in=(self.request.user.shopping_cart.recipe.values('id'))
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        filename = f'{request.user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок \n'
            f'{timezone.now().strftime(DATE_FORMAT)}\n'
        )
        for recipe in ingredient:
            shopping_list += (
                f' {recipe["ingredient__name"]} - '
                f'{recipe["amount"]} '
                f'{recipe["ingredient__measurement_unit"]}.'
            )

        shopping_list += '\n\nПосчитано в Foodgram'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class TagsViewSet(
        PermissionAndPaginationMixin,
        viewsets.ModelViewSet):
    """Список тэгов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(
        PermissionAndPaginationMixin,
        viewsets.ModelViewSet):
    """Список ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class AddAndDeleteSubscribe(
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView):
    """Подписка и отписка от пользователя."""

    serializer_class = FollowersSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following'
        ).prefetch_related(
            'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True), )

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'На самого себя не подписаться!'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.user.follower.filter(author=instance).exists():
            return Response(
                {'errors': 'Уже подписан!'},
                status=status.HTTP_400_BAD_REQUEST)
        subs = request.user.follower.create(author=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UsersViewSet(UserViewSet):
    """Пользователи."""

    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.follower.filter(
                    author=OuterRef('id'))
            )).prefetch_related(
                'follower', 'following'
        ) if self.request.user.is_authenticated else User.objects.annotate(
            is_subscribed=Value(False))

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получить на кого пользователь подписан."""

        queryset = Followers.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowersSerializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class GetObjectMixin:
    """Миксина для удаления/добавления рецептов избранных/корзины."""

    serializer_class = SubscribeRecipeSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)

        return recipe


class AddDeleteShoppingCart(
        GetObjectMixin,
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView
):
    """Добавление и удаление рецепта в/из корзины."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


class AddDeleteFavoriteRecipe(
        GetObjectMixin,
        generics.RetrieveDestroyAPIView,
        generics.ListCreateAPIView
):
    """Добавление и удаление рецепта в/из избранных."""

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)


@api_view(['post'])
def set_password(request):
    """Изменить пароль."""

    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введите верные данные!'},
        status=status.HTTP_400_BAD_REQUEST)
