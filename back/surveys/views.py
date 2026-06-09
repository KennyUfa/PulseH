from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import status
from .models import Survey, SurveyResponse
from .serializers import SurveySerializer, SurveyResponseSerializer, SurveyResponseDetailSerializer


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_hr)


class SurveyViewSet(ModelViewSet):
    serializer_class = SurveySerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'respond', 'my_response'):
            return [IsAuthenticated()]
        return [IsHR()]

    def get_queryset(self):
        return Survey.objects.prefetch_related('questions__options').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        survey = self.get_object()
        if survey.status != Survey.STATUS_ACTIVE:
            return Response({'detail': 'Опрос недоступен для прохождения'}, status=status.HTTP_400_BAD_REQUEST)
        if SurveyResponse.objects.filter(survey=survey, user=request.user).exists():
            return Response({'detail': 'Вы уже прошли этот опрос'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SurveyResponseSerializer(
            data=request.data,
            context={'survey': survey, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Ответы сохранены'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='my_response')
    def my_response(self, request, pk=None):
        survey = self.get_object()
        if survey.is_anonymous:
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        response = SurveyResponse.objects.filter(
            survey=survey, user=request.user
        ).prefetch_related('answers__selected_options').first()
        if not response:
            return Response(None, status=status.HTTP_204_NO_CONTENT)
        return Response(SurveyResponseDetailSerializer(response).data)
