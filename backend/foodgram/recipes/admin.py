from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag)


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'name',
            'text',
            'author',
            'cooking_time',
            'count_fans',
        )
    list_editable = (
            'name',
            'text',
            'cooking_time',
        )
    inlines = (IngredientAmountInline,)
    filter_horizontal = ('tags',)
    list_filter = ('name', 'author', 'tags')

    def count_fans(self, obj):
        return obj.favorites.all().count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_editable = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
