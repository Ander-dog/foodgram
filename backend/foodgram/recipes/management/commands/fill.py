import base64
import json

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django.shortcuts import get_object_or_404

from api.serializers import (IngredientSerializer, TagSerializer,
                             UserSerializer, RecipeInteractSerializer)
from recipes.models import Ingredient, Tag


User = get_user_model()
DATA_PATH = 'data/models/'


class Command(BaseCommand):
    def fill_ingredients(self):
        with open(DATA_PATH + 'ingredients.json') as file:
            ingredients_data = json.load(file)
            for ingr in ingredients_data:
                ingredient = IngredientSerializer(data=ingr)
                if ingredient.is_valid(raise_exception=True):
                    ingredient.save()
    
    def fill_tags(self):
        with open(DATA_PATH + 'tags.json') as file:
            tags_data = json.load(file)
            for tag in tags_data:
                tag = TagSerializer(data=tag)
                if tag.is_valid(raise_exception=True):
                    tag.save()
    
    def fill_users(self):
        with open(DATA_PATH + 'users.json') as file:
            users_data = json.load(file)
            for user in users_data:
                user = UserSerializer(data=user)
                if user.is_valid(raise_exception=True):
                    user.save()

    def fill_recipes(self):
        with open(DATA_PATH + 'recipes.json') as file:
            recipes_data = json.load(file)
            for recipe in recipes_data:
                author = get_object_or_404(User, username=recipe['author'])
                recipe['author'] = author.id
                tags = []
                for tag in recipe['tags']:
                    tag_id = get_object_or_404(Tag, slug=tag).id
                    tags.append(tag_id)
                recipe['tags'] = tags
                for ingr in recipe['ingredients']:
                    ingredient = get_object_or_404(
                        Ingredient,
                        name=ingr['name']
                    )
                    ingr['id'] = ingredient.id
                with open(DATA_PATH + recipe['image'], 'rb') as image_file:
                    image_bytes = base64.b64encode(image_file.read())
                    image_str = image_bytes.decode()
                    recipe['image'] = image_str
                recipe = RecipeInteractSerializer(data=recipe)
                if recipe.is_valid(raise_exception=True):
                    recipe.save()

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '-u',
            '--users',
            action='store_true',
            help='Fills the data base with users',
        )
        parser.add_argument(
            '-i',
            '--ingredients',
            action='store_true',
            help='Fills the data base with ingredients',
        )
        parser.add_argument(
            '-t',
            '--tags',
            action='store_true',
            help='Fills the data base with tags',
        )
        parser.add_argument(
            '-r',
            '--recipes',
            action='store_true',
            help='Fills the data base with recipes',
        )
        parser.add_argument(
            '-a',
            '--all',
            action='store_true',
            help='Fills the data base with all objects',
        )
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        if options['all'] or options['users']:
            self.fill_users()
            self.stdout.write(self.style.SUCCESS('Все пользователи загружены!'))
        if options['all'] or options['tags']:
            self.fill_tags()
            self.stdout.write(self.style.SUCCESS('Все тэги загружены!'))
        if options['all'] or options['ingredients']:
            self.fill_ingredients()
            self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))
        if options['all'] or options['recipes']:
            self.fill_recipes()
            self.stdout.write(self.style.SUCCESS('Все рецепты загружены!'))
