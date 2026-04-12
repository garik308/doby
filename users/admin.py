from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import City, User


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'translit')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'translit')
    ordering = ('name',)


@admin.register(User)
class MyUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'full_name', 'phone', 'city', 'is_staff', 'date_joined')
    list_display_links = ('id', 'username')
    list_filter = ('is_staff', 'is_active', 'city', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('uuid', 'patronymic', 'phone', 'avatar', 'city', 'bio', 'sitter_profile')}),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'uuid')
