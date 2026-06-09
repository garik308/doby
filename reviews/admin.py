from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'reviewer', 'sitter', 'rating', 'comment',)
    readonly_fields = ('dt_created', 'dt_updated',)