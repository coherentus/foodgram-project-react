from django.contrib import admin

from .models import Component, Product, Recipe, Tag


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    ordering = ('name',)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ('product', 'amount',)
    list_filter = ('product__name',)
    search_fields = ('product',)
    ordering = ('product',)


class ComponentRecipeInline(admin.TabularInline):
    model = Component
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (ComponentRecipeInline,)
    readonly_fields = ('pub_date', 'in_favor_count', )
    fields = (
        'in_favor_count', 'pub_date', 'author', 'title', 'text',
        'picture', 'tags', 'cooking_time'
    )

    list_display = ('title', 'author', 'in_favor_count')
    list_display_links = ('title',)
    list_filter = ('author', 'title', 'tags')
    search_fields = ('title', 'author', 'tags',)
    ordering = ('pub_date',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)
    search_fields = ('name', 'slug',)
    ordering = ('name',)
