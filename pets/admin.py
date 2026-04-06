from django.contrib import admin

from pets.models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet_type', 'name', 'age', 'owner', 'dt_created', 'dt_updated')
    list_display_links = ('id', 'name')
    list_filter = ('pet_type', 'dt_created', 'dt_updated')
    search_fields = ('name', 'owner__username', 'owner__first_name', 'owner__last_name')
    readonly_fields = ('dt_created', 'dt_updated')
    ordering = ('name',)
