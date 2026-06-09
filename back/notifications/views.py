from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import PushSubscription


class VapidPublicKeyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'public_key': settings.VAPID_PUBLIC_KEY})


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        endpoint = request.data.get('endpoint')
        p256dh = request.data.get('p256dh')
        auth = request.data.get('auth')
        if not all([endpoint, p256dh, auth]):
            return Response({'detail': 'endpoint, p256dh и auth обязательны'}, status=400)

        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={'user': request.user, 'p256dh': p256dh, 'auth': auth},
        )
        return Response({'detail': 'Подписка сохранена'}, status=201)


class UnsubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response({'detail': 'endpoint обязателен'}, status=400)
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        return Response({'detail': 'Подписка удалена'})
