from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (AddAndDelSubscribe, AddDelFavoriteRecipe,
                    AddDelShoppingCart, AuthToken, IngredientsViewSet,
                    RecipesViewSet, TagsViewSet, UsersViewSet, set_password)

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet)
router.register('tags', TagsViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('recipes', RecipesViewSet)


urlpatterns = [
    # path(
    #     'auth/token/login/',
    #     AuthToken.as_view(),
    #     name='login'),
    # path(
    #     'users/set_password/',
    #     set_password,
    #     name='set_password'),
    path(
        'users/<int:user_id>/subscribe/',
        AddAndDelSubscribe.as_view(),
        name='subscribe'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        AddDelFavoriteRecipe.as_view(),
        name='favorite_recipe'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        AddDelShoppingCart.as_view(),
        name='shopping_cart'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls'))
]
