from django.urls import include, path
from rest_framework import routers

from .views import (TagViewSet, IngredientViewSet, FavoriteAPIView,
                    ShoppingCartAPIView, SubscribeAPIView, RecipeViewSet,
                    UserViewSet, SubscriptionAPIView)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteAPIView.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorites'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartAPIView.as_view({'post': 'create', 'delete': 'destroy'}),
        name='shopping_cart'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeAPIView.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribes'
    ),
    path(
        'users/subscriptions/',
        SubscriptionAPIView.as_view(),
        name='subscriptions'
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
