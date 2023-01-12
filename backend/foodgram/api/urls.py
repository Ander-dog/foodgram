from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, FavoriteViewSet,
                    ShoppingCartViewSet, SubscribeViewSet, RecipeViewSet,
                    UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite',
                FavoriteViewSet, basename='favorites')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shopping_cart')
router.register(r'users/(?P<user_id>\d+)/subscribe',
                SubscribeViewSet, basename='shopping_cart')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
