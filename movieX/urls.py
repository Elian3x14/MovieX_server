from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def index_view(request):
    from django.http import HttpResponse
    return HttpResponse("""
                        <h1>Welcome to MovieX API</h1>
                        <p>Visit <a href="/api/docs/">API Documentation</a> for more details.</p>
                        <p>Check out the <a href="/api/redoc/">ReDoc Documentation</a> for a detailed API reference.</p>
                        <p>Use the <a href="/api/schema/">OpenAPI Schema</a> to explore the API endpoints.</p>
                        <p>For Swagger UI, go to <a href="/api/docs/">Swagger UI</a>.</p>
                        <p>Admin panel is available at <a href="/admin/">Admin Panel</a>.</p>
                        """)

urlpatterns = [
    path('', index_view, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

