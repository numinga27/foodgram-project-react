from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AddAndDeleteSubscribe, AddDeleteFavoriteRecipe,
                    AddDeleteShoppingCart, IngredientsViewSet, RecipesViewSet,
                    TagsViewSet, UsersViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet, basename='user')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path(
        'users/<int:user_id>/subscribe/',
        AddAndDeleteSubscribe.as_view(),
        name='subscribe'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        AddDeleteFavoriteRecipe.as_view(),
        name='favorite_recipe'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        AddDeleteShoppingCart.as_view(),
        name='shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls'))
]
