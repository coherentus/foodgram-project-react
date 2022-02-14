from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from users.models import CustomUser as User


class ProductSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeQueryParamFilter(FilterSet):
    """Get qs based on 'query_params'. Return it.

    Possible params are:
    'is_favorited'          boolean
    'is_in_shopping_cart'   boolean
    'author'                Recipe.author field
    'tags'                  Recipe.tags field
    """
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Make qs of current user's favorites if value True/1."""
        if value and not self.request.user.is_anonymous:
            return queryset.filter(
                favourite__user=self.request.user
            ).prefetch_related('components')
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Make qs of current user's bascket if value True/1."""
        if value and not self.request.user.is_anonymous:
            return queryset.filter(
                bascket_recipes__user=self.request.user
            ).prefetch_related('components')
        return queryset
