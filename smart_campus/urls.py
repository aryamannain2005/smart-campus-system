"""
URL configuration for Smart Campus Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/attendance/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    path('attendance/', include('attendance.urls')),
    path('api/', include('api.urls')),
    path('notifications/', include('notifications.urls')),
    path('face-recognition/', include('face_recognition.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
