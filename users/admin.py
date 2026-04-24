from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from pets.models import Pet
from users.models import City, User, DeletedUser, UserPhoto


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'translit')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'translit')
    ordering = ('name',)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'full_name', 'phone', 'city', 'is_staff', 'date_joined')
    list_display_links = ('id', 'username')
    list_filter = ('is_staff', 'is_active', 'city', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('uuid', 'patronymic', 'phone', 'avatar', 'city', 'bio')}),
    )
    readonly_fields = ('date_joined', 'last_login', 'uuid')


@admin.register(UserPhoto)
class UserPhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'image', 'order_number', 'is_main')
    list_select_related = ('user',)
    list_filter = ('dt_created', 'dt_updated')
    search_fields = ('user',)
    raw_id_fields = ('user',)
    readonly_fields = ('dt_created', 'dt_updated')


@admin.register(DeletedUser)
class DeletedUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'phone', 'full_name', 'city')
    search_fields = ('uuid', 'username', 'phone', 'user_id')
    readonly_fields = ('dt_created', 'dt_updated', 'uuid', 'user_id')
