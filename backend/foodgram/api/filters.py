from django.core.exceptions import ValidationError
import django_filters as filters
from django_filters import rest_framework as django_filters
from django.db.models import Q

from users.models import User
from posts.models import Ingredient, Recipe


class TagsMultipleChoiceField(
        filters.fields.MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'],
                code='required')
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},)


class TagsFilter(filters.AllValuesMultipleFilter):
    field_class = TagsMultipleChoiceField


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


# class RecipeFilter(django_filters.FilterSet):
#     tags = django_filters.CharFilter(
#         field_name='tags__slug', method='filter_tags', lookup_expr='in')
#     is_in_shopping_cart = django_filters.BooleanFilter(
#         field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')
#     is_favorited = django_filters.BooleanFilter(
#         field_name='is_favorited', method='filter_is_favorited')

#     def filter_tags(self, queryset, name, value):
#         values = self.request.GET.getlist(key='tags', default=[])

#         if not value:
#             return queryset

#         queries = [Q(tags__slug=value) for value in values]

#         query = queries.pop()
#         for item in queries:
#             query |= item

#         return queryset.filter(query).distinct()

#     def __is_something(self, queryset, name, value, related_field):
#         if self.request.user.is_anonymous:
#             return Recipe.objects.none() if value else queryset

#         objects = getattr(self.request.user, related_field).all()
#         return queryset.filter(pk__in=[item.recipe.pk for item in objects])

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         return self.__is_something(queryset, name, value, 'shopping_cart')

#     def filter_is_favorited(self, queryset, name, value):
#         return self.__is_something(queryset, name, value, 'favorites')

#     class Meta:
#         model = Recipe
#         fields = ('author',)

class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В корзине.')
    is_favorited = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget(),
        label='В избранных.')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

