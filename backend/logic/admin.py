from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Basket, FavourRecipe, Follow


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipes_count')
    list_display_links = ('user', )
    list_filter = ('user', )
    fieldsets = (
        (None, {'fields': ('user', 'recipe')}),
    )
    search_fields = ('user__username', )
    ordering = ('user', )


@admin.register(FavourRecipe)
class FavourRecipesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'recipes_count')
    list_display_links = ('user', )
    list_filter = ('user', )
    fieldsets = (
        (None, {'fields': ('user', 'recipe')}),
    )
    search_fields = ('user__username', )
    ordering = ('user', )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'folowing_count', 'folower_count')
    list_display_links = ('user',)
    list_filter = ('user', 'author')
    fieldsets = (
        (None, {'fields': ('user', 'author')}),
    )
    search_fields = ('user__username', 'following__username')
    ordering = ('user', 'author',)
