from django.db import models
from users.models import User


class Survey(models.Model):
    # Возможные статусы опроса
    STATUS_DRAFT = 'draft'        # Черновик — не виден сотрудникам
    STATUS_ACTIVE = 'active'      # Активный — доступен для прохождения
    STATUS_COMPLETED = 'completed' # Завершён — приём ответов закрыт
    STATUS_ARCHIVED = 'archived'  # Архив — скрыт из основных списков
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_ACTIVE, 'Активный'),
        (STATUS_COMPLETED, 'Завершён'),
        (STATUS_ARCHIVED, 'Архив'),
    ]

    title = models.CharField(max_length=255)           # Название опроса
    description = models.TextField(blank=True)         # Описание / инструкция для сотрудника
    is_anonymous = models.BooleanField(default=False)  # Если True — ответы не привязываются к пользователю
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(                    # HR, создавший опрос
        User, on_delete=models.SET_NULL, null=True, related_name='surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Новые опросы сверху

    def __str__(self):
        return self.title


class Question(models.Model):
    TYPE_SINGLE = 'single'
    TYPE_MULTIPLE = 'multiple'
    TYPE_SCALE = 'scale'
    TYPE_TEXT = 'text'
    TYPE_NPS = 'nps'
    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Один вариант'),
        (TYPE_MULTIPLE, 'Несколько вариантов'),
        (TYPE_SCALE, 'Шкала 1-10'),
        (TYPE_TEXT, 'Текстовый ответ'),
        (TYPE_NPS, 'NPS (0-10)'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_SINGLE)
    order = models.PositiveIntegerField(default=0)
    # Условная логика: показывать вопрос только если у вопроса с указанным индексом выбран вариант с указанным текстом
    condition_question_index = models.IntegerField(null=True, blank=True)
    condition_option_text = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class AnswerOption(models.Model):
    # Вариант ответа, который видит сотрудник при прохождении опроса
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)          # Текст варианта ответа
    order = models.PositiveIntegerField(default=0)   # Порядок отображения среди вариантов

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class SurveyResponse(models.Model):
    # Одно прохождение опроса одним пользователем
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(                        # Null для анонимных опросов
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='responses'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response to "{self.survey}" by {self.user or "anonymous"}'


class Answer(models.Model):
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    text_answer = models.CharField(max_length=2000, blank=True, default='')

    def __str__(self):
        return f'Answer to "{self.question}"'
