from django.contrib import admin

from pets.models import Pet, PetPhoto


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pet_type', 'age', 'owner', 'breed_name', 'dt_created', 'dt_updated')
    list_display_links = ('name',)
    list_filter = ('pet_type', 'dt_created', 'dt_updated')
    search_fields = ('name', 'owner__username', 'owner__first_name', 'owner__last_name')
    readonly_fields = ('dt_created', 'dt_updated')
    raw_id_fields = ('owner',)
    ordering = ('name',)


@admin.register(PetPhoto)
class PetPhotoAdmin(admin.ModelAdmin):
    list_display = ('pet', 'image', 'order_number', 'is_main')
    list_filter = ('dt_created', 'dt_updated')
    search_fields = ('pet',)
    readonly_fields = ('dt_created', 'dt_updated')
