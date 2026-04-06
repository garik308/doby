from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'owner', 'sitter', 'pet', 'start_datetime', 'end_datetime', 
        'status', 'dt_created', 'dt_updated'
    )
    list_display_links = ('id',)
    list_filter = ('status', 'start_datetime', 'dt_created', 'dt_updated')
    search_fields = ('owner__username', 'sitter__username', 'pet__name', 'comment')
    readonly_fields = ('dt_created', 'dt_updated', 'sitter_confirmed_at')
    ordering = ('-dt_created',)
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'sitter', 'pet', 'status')
        }),
        ('Время бронирования', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Дополнительно', {
            'fields': ('comment', 'sitter_confirmed_at')
        }),
        ('Системные поля', {
            'fields': ('dt_created', 'dt_updated'),
            'classes': ('collapse',)
        }),
    )

