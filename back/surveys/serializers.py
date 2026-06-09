from rest_framework import serializers
from .models import Survey, Question, AnswerOption, SurveyResponse, Answer


class AnswerOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

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
                  'start_date', 'end_date',
                  'created_by', 'created_at', 'questions', 'has_responded')
        read_only_fields = ('id', 'created_by', 'created_at', 'has_responded')

    def get_has_responded(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.responses.filter(user=request.user).exists()

    def _save_options(self, question, options_data):
        existing_opts = {o.id: o for o in question.options.all()}
        seen_opt_ids = set()
        new_opts = []
        for j, o_data in enumerate(options_data):
            o_id = o_data.get('id')
            text = o_data.get('text', '')
            order = o_data.get('order', j)
            if o_id and o_id in existing_opts:
                opt = existing_opts[o_id]
                opt.text = text
                opt.order = order
                opt.save(update_fields=['text', 'order'])
                seen_opt_ids.add(o_id)
            else:
                new_opts.append(AnswerOption(question=question, text=text, order=order))
        if new_opts:
            AnswerOption.objects.bulk_create(new_opts)
        # Only delete options not referenced by existing answers
        opts_to_delete = set(existing_opts) - seen_opt_ids
        if opts_to_delete:
            referenced_ids = set(
                Answer.objects.filter(selected_options__id__in=opts_to_delete)
                .values_list('selected_options__id', flat=True)
            )
            safe_to_delete = opts_to_delete - referenced_ids
            if safe_to_delete:
                AnswerOption.objects.filter(id__in=safe_to_delete).delete()

    def update(self, instance, validated_data):
        old_status = instance.status
        questions_data = validated_data.pop('questions', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if old_status != 'active' and instance.status == 'active':
            try:
                from notifications.push import send_push_to_all
                send_push_to_all(instance)
            except Exception:
                pass
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
                self._save_options(question, options_data)
            ids_to_delete = set(existing) - seen_ids
            if ids_to_delete:
                instance.questions.filter(id__in=ids_to_delete).delete()
        return instance

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        survey = Survey.objects.create(**validated_data)
        for i, q_data in enumerate(questions_data):
            q_data.pop('id', None)
            options_data = q_data.pop('options', [])
            q_data.setdefault('order', i)
            question = Question.objects.create(survey=survey, **q_data)
            AnswerOption.objects.bulk_create([
                AnswerOption(question=question, text=o.get('text', ''), order=o.get('order', j))
                for j, o in enumerate(options_data)
            ])
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

    def validate_answers(self, value):
        survey = self.context['survey']
        valid_ids = set(survey.questions.values_list('id', flat=True))
        for ans in value:
            if ans['question'].id not in valid_ids:
                raise serializers.ValidationError(
                    f'Вопрос {ans["question"].id} не принадлежит этому опросу.'
                )
        return value

    def create(self, validated_data):
        survey = self.context['survey']
        request = self.context['request']
        response = SurveyResponse.objects.create(survey=survey, user=request.user)
        for a in validated_data['answers']:
            answer = Answer.objects.create(
                response=response,
                question=a['question'],
                text_answer=a.get('text_answer', ''),
            )
            answer.selected_options.set(a.get('selected_options', []))
        return response
