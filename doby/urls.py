from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from doby.views import health_check, AdminProtectedSpectacularAPIView, AdminProtectedSpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/users/', include('users.urls')),
    path('api/sitters/', include('sitters.urls')),
    path('api/chat/', include('chats.urls')),
    path('api/pets/', include('pets.urls')),
    path('health/', health_check),
    path('api/schema/', AdminProtectedSpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', AdminProtectedSpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
