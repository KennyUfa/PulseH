from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from surveys.models import Survey
from users.models import User


class SurveyResultsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_hr:
            return Response({'detail': 'Доступ запрещён'}, status=403)

        surveys = Survey.objects.all().order_by('-created_at')
        total_users = User.objects.filter(is_active=True).count()

        result = []
        for s in surveys:
            completed = s.responses.count()
            result.append({
                'id': s.id,
                'title': s.title,
                'status': s.status,
                'is_anonymous': s.is_anonymous,
                'total_users': total_users,
                'completed_count': completed,
                'not_completed_count': max(0, total_users - completed),
            })
        return Response(result)


class SurveyResultsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_hr:
            return Response({'detail': 'Доступ запрещён'}, status=403)

        try:
            survey = Survey.objects.prefetch_related(
                'questions__options',
                'responses__answers__selected_options',
                'responses__answers__question',
                'responses__user',
            ).get(pk=pk)
        except Survey.DoesNotExist:
            return Response({'detail': 'Не найден'}, status=404)

        total_users = User.objects.filter(is_active=True).count()
        completed = survey.responses.count()

        responses = []
        for resp in survey.responses.all():
            answers = []
            for ans in resp.answers.select_related('question').prefetch_related('selected_options').all():
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
