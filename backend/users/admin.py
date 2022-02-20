from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.admin import TokenAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser

TokenAdmin.raw_id_fields = ['user']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        'email', 'username', 'first_name', 'follows',
        'is_staff', 'is_active'
    )
    list_display_links = ('email', 'username', 'first_name')
    list_filter = ('first_name', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password',
                           'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'username', 'is_staff', 'is_active', 'first_name', 'last_name'
            )
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
