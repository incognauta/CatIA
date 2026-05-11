from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserLLMSettingsViewSet

router = DefaultRouter()
router.register(r'llm-settings', UserLLMSettingsViewSet, basename='llm-settings')

urlpatterns = [
    path('', include(router.urls)),
]
