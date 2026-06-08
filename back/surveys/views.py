from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Survey
from .serializers import SurveySerializer


class SurveyViewSet(ModelViewSet):
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Survey.objects.prefetch_related('questions__options').all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
