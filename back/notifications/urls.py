from django.urls import path
from .views import VapidPublicKeyView, SubscribeView, UnsubscribeView

urlpatterns = [
    path('push/vapid-key/', VapidPublicKeyView.as_view()),
    path('push/subscribe/', SubscribeView.as_view()),
    path('push/unsubscribe/', UnsubscribeView.as_view()),
]
