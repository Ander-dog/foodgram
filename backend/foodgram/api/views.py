from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen.canvas import Canvas
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly, AuthorRegistrationOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeInteractSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)

User = get_user_model()


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class CreateDestroyAPIView(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('-id')
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter


class FavoriteAPIView(CreateDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        serializer.save(user=self.request.user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Favorite,
            recipe=self.kwargs['recipe_id'],
            user=request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartAPIView(CreateDestroyAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, id=self.kwargs['recipe_id'])
        serializer.save(user=self.request.user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(
            ShoppingCart,
            recipe=self.kwargs['recipe_id'],
            user=request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeAPIView(CreateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs['user_id'])
        serializer.save(user=self.request.user, author=author)

    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Subscription,
            author=self.kwargs['user_id'],
            user=request.user)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    serializer_class = RecipeInteractSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.prefetch_related(
            'tags',
            'ingredients',
        ).select_related('author')

        if user.is_authenticated:
            return queryset.annotate(
                is_favorited_field=Exists(Favorite.objects.filter(
                    user=user, recipe__id=OuterRef('id'))
                ),
                is_in_shopping_cart_field=Exists(ShoppingCart.objects.filter(
                    user=user, recipe__id=OuterRef('id'))
                )
            ).order_by('-id')

        return queryset.annotate(
            is_favorited_field=Value(False, output_field=BooleanField()),
            is_in_shopping_cart_field=Value(False, output_field=BooleanField())
        ).order_by('-id')

    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        show_serializer = RecipeReadSerializer(
            instance,
            context={'request': request},
        )
        headers = self.get_success_headers(show_serializer.data)
        return Response(
            show_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeInteractSerializer

    def canvas_method(self, list, title, filename):
        start_x, start_y = 40, 730
        response = HttpResponse(
            status=status.HTTP_200_OK,
            content_type='application/pdf',
        )
        response['Content-Disposition'] = (f'attachment; filename='
                                           f'"{filename}"')
        canvas = Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(
            ttfonts.TTFont('FreeSans', 'data/fonts/FreeSans.ttf')
        )
        canvas.setFont('FreeSans', 34)
        canvas.drawString(start_x - 10, start_y + 40, title)
        canvas.setFont('FreeSans', 18)
        for number, item in enumerate(list, start=1):
            if start_y < 100:
                start_y = 730
                canvas.showPage()
                canvas.setFont('FreeSans', 18)
            canvas.drawString(start_x, start_y, f'{number}. {item}')
            start_y -= 30
        canvas.showPage()
        canvas.save()
        return response

    @action(['get'], detail=False, url_path='download_shopping_cart',
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = IngredientAmount.objects.filter(
            recipe__is_in_shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            ingredient_amount=Sum('amount')
        )
        title = 'Список покупок:'
        filename = 'shopping-list.pdf'
        text_content = []
        for ingr in ingredients:
            name = ingr.get('ingredient__name')
            m_unit = ingr.get('ingredient__measurement_unit')
            amount = ingr.get('ingredient_amount')
            text_content.append(f'{name.capitalize()}: {amount} {m_unit}')

        return self.canvas_method(text_content, title, filename)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination
    permission_classes = (AuthorRegistrationOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if kwargs['partial']:
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(['get'], detail=False, url_path='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False, url_path='set_password',
            permission_classes=(IsAuthenticated,))
    def set_password(self, request, *args, **kwargs):
        user = request.user
        serializer = SetPasswordSerializer(data=request.data)

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


class SubscriptionAPIView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
