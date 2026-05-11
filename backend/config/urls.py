from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def health_check(_request):
    return JsonResponse({"status": "ok", "service": "pdf_ia_rework_backend"})

urlpatterns = [
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    # Ver: docs/07_contratos_api.md (endpoints planificados)
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.notebooks.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.chat.urls")),
    path("api/v1/", include("apps.core.urls")),
]
