from rest_framework import serializers
from .models import Survey, Question, AnswerOption, SurveyResponse, Answer


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ('id', 'text', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    options = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'order', 'options',
                  'condition_question_index', 'condition_option_text')


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    created_by = serializers.StringRelatedField(read_only=True)
    has_responded = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'is_anonymous', 'status',
                  'created_by', 'created_at', 'questions', 'has_responded')
        read_only_fields = ('id', 'created_by', 'created_at', 'has_responded')

    def get_has_responded(self, obj):
        request = self.context.get('request')
        if not request or obj.is_anonymous:
            return False
        return obj.responses.filter(user=request.user).exists()

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            existing = {q.id: q for q in instance.questions.all()}
            seen_ids = set()
            for i, q_data in enumerate(questions_data):
                q_id = q_data.pop('id', None)
                options_data = q_data.pop('options', [])
                q_data['order'] = i
                if q_id and q_id in existing:
                    question = existing[q_id]
                    for attr, val in q_data.items():
                        setattr(question, attr, val)
                    question.save()
                    seen_ids.add(q_id)
                else:
                    question = Question.objects.create(survey=instance, **q_data)
                question.options.all().delete()
                for j, o_data in enumerate(options_data):
                    o_data.setdefault('order', j)
                    AnswerOption.objects.create(question=question, **o_data)
            ids_to_delete = set(existing) - seen_ids
            if ids_to_delete:
                instance.questions.filter(id__in=ids_to_delete).delete()
        return instance

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        survey = Survey.objects.create(**validated_data)
        for i, q_data in enumerate(questions_data):
            options_data = q_data.pop('options', [])
            q_data.setdefault('order', i)
            question = Question.objects.create(survey=survey, **q_data)
            for j, o_data in enumerate(options_data):
                o_data.setdefault('order', j)
                AnswerOption.objects.create(question=question, **o_data)
        return survey


class AnswerDetailSerializer(serializers.ModelSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ('question', 'selected_options', 'text_answer')


class SurveyResponseDetailSerializer(serializers.ModelSerializer):
    answers = AnswerDetailSerializer(many=True)

    class Meta:
        model = SurveyResponse
        fields = ('id', 'submitted_at', 'answers')


class AnswerSubmitSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_options = serializers.PrimaryKeyRelatedField(
        queryset=AnswerOption.objects.all(), many=True, required=False, default=list
    )
    text_answer = serializers.CharField(required=False, allow_blank=True, default='')


class SurveyResponseSerializer(serializers.Serializer):
    answers = AnswerSubmitSerializer(many=True)

    def create(self, validated_data):
        survey = self.context['survey']
        request = self.context['request']
        user = None if survey.is_anonymous else request.user

        response = SurveyResponse.objects.create(survey=survey, user=user)
        for a in validated_data['answers']:
            answer = Answer.objects.create(
                response=response,
                question=a['question'],
                text_answer=a.get('text_answer', ''),
            )
            answer.selected_options.set(a.get('selected_options', []))
        return response
