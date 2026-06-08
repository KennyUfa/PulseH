from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Survey
from .serializers import SurveySerializer, SurveyResponseSerializer


class SurveyViewSet(ModelViewSet):
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Survey.objects.prefetch_related('questions__options').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        survey = self.get_object()
        if survey.status != Survey.STATUS_ACTIVE:
            return Response({'detail': 'Опрос недоступен для прохождения'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SurveyResponseSerializer(
            data=request.data,
            context={'survey': survey, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Ответы сохранены'}, status=status.HTTP_201_CREATED)
