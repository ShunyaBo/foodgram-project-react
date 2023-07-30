from django_filters.rest_framework import filters, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filters(favorite__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset


class IngredientFilter(FilterSet):
    """Поиск о частичному вхождению в начале названия ингредиента."""
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
# class IngredientSearchFilter(SearchFilter):
#     search_param = 'name'

# class IngredientFilter(FilterSet):
#     name = filters.CharFilter(method='search_ingredients')

#     class Meta:
#         model = Ingredient
#         fields = ('name',)

#     def search_ingredients(self, queryset, name, value):
#         if not value:
#             return queryset
#         start_with_queryset = queryset.filter(
#             name__istartswith=value
#         ).annotate(order=Value(0, IntegerField()))
#         contain_queryset = (
#             queryset.filter(name__icontains=value)
#             .exclude(
#                 pk__in=(ingredient.pk for ingredient in start_with_queryset)
#             )
#             .annotate(order=Value(1, IntegerField()))
#         )
#         return start_with_queryset.union(contain_queryset).order_by("order")
