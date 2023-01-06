from django.contrib import admin

from .models import Recipts_Ingredients


class Recipe_Ingredient_Admin(admin.StackedInline):
    model = Recipts_Ingredients
    autocomplete_fields = ('ingredient',)
