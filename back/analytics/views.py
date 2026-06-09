from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count
from surveys.models import Survey
from users.models import User


class IsHRPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_hr


class SurveyResultsListView(APIView):
    permission_classes = [IsHRPermission]

    def get(self, request):
        total_users = User.objects.filter(is_active=True).count()
        surveys = (
            Survey.objects
            .annotate(completed_count=Count('responses'))
            .order_by('-created_at')
        )
        result = [
            {
                'id': s.id,
                'title': s.title,
                'status': s.status,
                'is_anonymous': s.is_anonymous,
                'total_users': total_users,
                'completed_count': s.completed_count,
                'not_completed_count': max(0, total_users - s.completed_count),
            }
            for s in surveys
        ]
        return Response(result)


class SurveyResultsDetailView(APIView):
    permission_classes = [IsHRPermission]

    def get(self, request, pk):
        try:
            survey = Survey.objects.prefetch_related(
                'questions__options',
                'responses__answers__selected_options',
                'responses__answers__question',
                'responses__user',
            ).get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Не найден'}, status=status.HTTP_404_NOT_FOUND)

        total_users = User.objects.filter(is_active=True).count()
        completed = len(survey.responses.all())

        responses = []
        for resp in survey.responses.all():
            answers = []
            for ans in resp.answers.all():
                answers.append({
                    'question_id': ans.question_id,
                    'question_text': ans.question.text,
                    'question_type': ans.question.question_type,
                    'selected_options': [opt.text for opt in ans.selected_options.all()],
                    'text_answer': ans.text_answer,
                })

            user_data = None
            if not survey.is_anonymous and resp.user:
                u = resp.user
                user_data = {
                    'id': u.id,
                    'name': f'{u.first_name} {u.last_name}'.strip() or u.phone_number,
                    'phone': u.phone_number,
                }

            responses.append({
                'id': resp.id,
                'submitted_at': resp.submitted_at,
                'user': user_data,
                'answers': answers,
            })

        questions = [
            {'id': q.id, 'text': q.text, 'question_type': q.question_type}
            for q in survey.questions.all()
        ]

        return Response({
            'id': survey.id,
            'title': survey.title,
            'description': survey.description,
            'status': survey.status,
            'is_anonymous': survey.is_anonymous,
            'total_users': total_users,
            'completed_count': completed,
            'not_completed_count': max(0, total_users - completed),
            'questions': questions,
            'responses': responses,
        })
