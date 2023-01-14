from django.contrib import admin

from .models import Recipies_Ingredients


class Recipe_Ingredient_Admin(admin.StackedInline):
    model = Recipies_Ingredients
    autocomplete_fields = ('ingredient',)
