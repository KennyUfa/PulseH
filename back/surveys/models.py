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
    # Тип вопроса определяет, сколько вариантов может выбрать сотрудник
    TYPE_SINGLE = 'single'      # Один вариант (radio)
    TYPE_MULTIPLE = 'multiple'  # Несколько вариантов (checkbox)
    TYPE_CHOICES = [
        (TYPE_SINGLE, 'Один вариант'),
        (TYPE_MULTIPLE, 'Несколько вариантов'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)  # Текст вопроса
    question_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_SINGLE)
    order = models.PositiveIntegerField(default=0)    # Порядок отображения в опросе

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
