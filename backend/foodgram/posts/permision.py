from django.contrib import admin

from .models import RecipiesIngredients


class RecipeIngredientAdmin(admin.StackedInline):
    model = RecipiesIngredients
    autocomplete_fields = ('ingredient',)
