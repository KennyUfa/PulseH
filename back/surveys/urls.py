from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet

router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')

urlpatterns = [
    path('', include(router.urls)),
]
