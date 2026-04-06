from django.contrib import admin

from chats.models import ChatRoom, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'is_read', 'dt_created', 'dt_updated')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'get_participants_count', 'dt_created', 'dt_updated')
    list_display_links = ('id',)
    list_filter = ('dt_created', 'dt_updated')
    search_fields = ('booking__id', 'participants__username')
    readonly_fields = ('dt_created', 'dt_updated')
    ordering = ('-dt_created',)
    inlines = [MessageInline]
    
    @admin.display(description='Участники')
    def get_participants_count(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'text', 'is_read', 'dt_created', 'dt_updated')
    list_display_links = ('id',)
    list_filter = ('is_read', 'dt_created', 'dt_updated')
    search_fields = ('text', 'sender__username', 'chat__booking__id')
    readonly_fields = ('dt_created', 'dt_updated')
    ordering = ('-dt_created',)
    date_hierarchy = 'dt_created'
