from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscription

from .filters import RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          PasswordSerializer, RecipeInteractSerializer,
                          RecipeReadSerializer, ShoppingCartSerializer,
                          SubscribeSerializator, SubscriptionSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteViewSet(CreateDestroyViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        serializer.save(author=self.request.user, recipe=recipe)


class ShoppingCartViewSet(CreateDestroyViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        serializer.save(author=self.request.user, recipe=recipe)


class SubscribeViewSet(CreateDestroyViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializator
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs['user_id'])
        serializer.save(user=self.request.user, author=author)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination = PageLimitPagination
    queryset = Recipe.objects.all()
    serializer_class = RecipeInteractSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeInteractSerializer

    @action(["get"], detail=False, url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(queryset)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination
    permission_classes = (AuthorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if kwargs['partial']:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(["get"], detail=False, url_path='subscriptions',
            permission_classes=(IsAuthenticated(),))
    def subscriptions(self, request, *args, **kwargs):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(queryset)
        return Response(serializer.data)

    @action(["get"], detail=False, url_path='me',
            permission_classes=(IsAuthenticated(),))
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(["post"], detail=False, url_path='set_password')
    def set_password(self, request, *args, **kwargs):
        user = request.user
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.data['current_password']
            if not user.check_password(current_password):
                return Response(
                    {'current_password': 'Неверный пароль'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
