from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crawler/', include('crawler.urls')),
    #Add URL maps to redirect the base URL to our application
    path('', RedirectView.as_view(url='/crawler/', permanent=True)),
    # Use static() to add url mapping to serve static files during development (only)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)