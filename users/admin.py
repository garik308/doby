from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import City, User

admin.site.register(City)

@admin.register(User)
class MyUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('patronymic', 'phone', 'avatar', 'city', 'bio', 'sitter_profile')}),
    )