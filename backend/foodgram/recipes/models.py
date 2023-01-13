from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    color = models.CharField(max_length=16)

    class Meta:
        verbose_name = 'Тэг'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единица измерения',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['measurement_unit', 'name'],
                name='unique ingredient')
        ]
        verbose_name = 'Ингридиент'

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        )
    text = models.TextField(
        verbose_name='Описание',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag)
    # ingredients = models.ManyToManyField(
    #     Ingredient,
    #     through='IngredientAmount',
    #     related_name='recipes'
    # )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Время приготовления',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique recipe')
        ]
        verbose_name = 'Рецепт'

    def __str__(self) -> str:
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингридиент'
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')
        ]
        verbose_name = 'Количество'

    def __str__(self) -> str:
        return f'{self.ingredient.name} {self.ingredient.measurement_unit}'


class Favorite(models.Model):

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique favorite')
        ]
        verbose_name = 'Избранное'

    def __str__(self) -> str:
        return self.recipe


class ShoppingCart(models.Model):

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopcart',
        verbose_name='Пользователь'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique purchase')
        ]
        verbose_name = 'Корзина'

    def __str__(self) -> str:
        return self.recipe
