from rest_framework import serializers
from .models import Survey, Question, AnswerOption, SurveyResponse, Answer


class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ('id', 'text', 'order')


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'order', 'options')


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'description', 'is_anonymous', 'status',
                  'created_by', 'created_at', 'questions')
        read_only_fields = ('id', 'created_by', 'created_at')

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if questions_data is not None:
            instance.questions.all().delete()
            for i, q_data in enumerate(questions_data):
                options_data = q_data.pop('options', [])
                q_data.setdefault('order', i)
                question = Question.objects.create(survey=instance, **q_data)
                for j, o_data in enumerate(options_data):
                    o_data.setdefault('order', j)
                    AnswerOption.objects.create(question=question, **o_data)
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
        fields = ('question', 'selected_options')


class SurveyResponseDetailSerializer(serializers.ModelSerializer):
    answers = AnswerDetailSerializer(many=True)

    class Meta:
        model = SurveyResponse
        fields = ('id', 'submitted_at', 'answers')


class AnswerSubmitSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_options = serializers.PrimaryKeyRelatedField(
        queryset=AnswerOption.objects.all(), many=True
    )


class SurveyResponseSerializer(serializers.Serializer):
    answers = AnswerSubmitSerializer(many=True)

    def create(self, validated_data):
        survey = self.context['survey']
        request = self.context['request']
        user = None if survey.is_anonymous else request.user

        response = SurveyResponse.objects.create(survey=survey, user=user)
        for a in validated_data['answers']:
            answer = Answer.objects.create(response=response, question=a['question'])
            answer.selected_options.set(a['selected_options'])
        return response
