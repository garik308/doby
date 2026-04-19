from django.contrib import admin

from chats.models import ChatRoom, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'text', 'short_original_filename', 'message_type', 'is_read', 'dt_created', 'dt_updated')
    readonly_fields = ('sender', 'text', 'short_original_filename', 'message_type', 'is_read', 'dt_created', 'dt_updated')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Сокращенное название файла')
    def short_original_filename(self, obj):
        if not obj.original_filename:
            return ''

        if len(obj.original_filename) < 30:
            return obj.original_filename

        filename, extension = obj.original_filename.split('.')
        return '...'.join([filename[:20], extension])


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'get_participants_count', 'dt_created', 'dt_updated')
    list_display_links = ('id',)
    list_filter = ('dt_created', 'dt_updated')
    search_fields = ('booking_id', 'participants__username')
    readonly_fields = ('dt_created', 'dt_updated')
    ordering = ('-dt_created',)
    inlines = [MessageInline]
    
    @admin.display(description='Участники')
    def get_participants_count(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'text', 'short_original_filename', 'message_type', 'is_read', 'dt_created', 'dt_updated')
    list_display_links = ('id',)
    list_filter = ('is_read', 'dt_created', 'dt_updated')
    list_select_related = ('sender', 'chat__booking')
    search_fields = ('text', 'sender__username', 'chat__booking__id')
    readonly_fields = ('dt_created', 'dt_updated', 'original_filename',)
    ordering = ('-dt_created',)
    date_hierarchy = 'dt_created'

    @admin.display(description='Сокращенное название файла')
    def short_original_filename(self, obj):
        if not obj.original_filename:
            return ''

        if len(obj.original_filename) < 30:
            return obj.original_filename

        filename, extension = obj.original_filename.split('.')
        return '...'.join([filename[:20], extension])

    def save_model(self, request, obj, form, change):
        if 'media_file' in form.changed_data and form.cleaned_data['media_file']:
            obj.original_filename = form.cleaned_data['media_file'].name
        super().save_model(request, obj, form, change)
