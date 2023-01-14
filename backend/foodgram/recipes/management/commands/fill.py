import json

from django.core.management import BaseCommand

from api.serializers import IngredientSerializer


class Command(BaseCommand):
    def fill_ingredients(self):
        with open('recipes/data/ingredients.json') as file:
            ingredients_data = json.load(file)
            for ingr in ingredients_data:
                ingredient = IngredientSerializer(data=ingr)
                if ingredient.is_valid(raise_exception=True):
                    ingredient.save()

    def handle(self, *args, **options):
        self.fill_ingredients()
