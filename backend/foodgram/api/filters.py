from django.contrib.auth import get_user_model
from django.db.models import IntegerField, Q, Value
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_boolean_status')
    is_in_shopping_cart = filters.BooleanFilter(method='get_boolean_status')

    def get_boolean_status(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            lookup = '__'.join([name, 'user'])
            return queryset.filter(**{lookup: self.request.user})
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(method='search_filter')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_filter(self, queryset, name, value):
        query = Q(name__istartswith=value)
        startswith_query = queryset.filter(
            query
        ).annotate(
            custom_order=Value(1, IntegerField())
        )
        query.add(~Q(name__icontains=value), Q.OR)
        query.negate()
        contains_query = queryset.filter(
            query
        ).annotate(
            custom_order=Value(2, IntegerField())
        )
        return startswith_query.union(contains_query).order_by(
            'custom_order', 'name'
        )
