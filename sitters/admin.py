from django.contrib import admin

from sitters.models import SitterProfile


@admin.register(SitterProfile)
class SitterProfileAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'experience_years', 'price_per_hour', 'is_verified', 'dt_created', 'dt_updated')
    list_display_links = ('uuid',)
    list_filter = ('is_verified', 'dt_created', 'dt_updated')
    search_fields = ('uuid', 'bio')
    readonly_fields = ('dt_created', 'dt_updated')
    ordering = ('-dt_created',)
