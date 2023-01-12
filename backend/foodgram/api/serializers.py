import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'is_subscribed',
        )

    def validate_username(self, value):
        if value != r'[\w.@+-]+\z':
            raise ValidationError('username не может быть "me"')
        return value

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'id',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializator(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault(),
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate_author(self, value):
        if value == self.context['request'].user:
            raise ValidationError(
                'На самого себя подписаться нельзя'
            )
        return value


class RecipeInteractSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'ltags',
            'author',
            'ingredients',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        queryset = obj.ingredients.all()
        return IngredientAmountSerializer(queryset, many=True).data

    def validate(self, attrs):
        ingredients = attrs['ingredients']
        tags = attrs['tags']
        ingredients_id = []
        for ingr in ingredients:
            if not Ingredient.objects.filter(id=ingr['id']).exists():
                raise ValidationError('Нет такого ингредиента')
            if ingr['id'] in ingredients_id:
                raise ValidationError('Повторяющийся ингредиент')
            ingredients_id.append(ingr['id'])
        for tag in tags:
            if not Tag.objects.filter(id=tag['id']).exists():
                raise ValidationError('Нет такого тэга')
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        for ingr in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingr['id'],
                amount=ingr['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingrdients')
        tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        instance.tags.clear()
        instance.tags.set(tags)

        instance.ingredients.all().delete()
        for ingr in ingredients:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient=ingr['id'],
                amount=ingr['amount'],
            )

        return super().update(instance, validated_data)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredient = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'text',
            'ltags',
            'author',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, obj):
        queryset = obj.ingredients.all()
        return IngredientAmountSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context['request']
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class PasswordSerializer(serializers.Serializer):

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
