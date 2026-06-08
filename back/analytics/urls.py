from django.urls import path
from .views import SurveyResultsListView, SurveyResultsDetailView

urlpatterns = [
    path('surveys/', SurveyResultsListView.as_view(), name='analytics-surveys'),
    path('surveys/<int:pk>/', SurveyResultsDetailView.as_view(), name='analytics-survey-detail'),
]
