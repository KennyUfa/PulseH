from django.core.management.base import BaseCommand
from django.utils import timezone
from surveys.models import Survey, Question, AnswerOption, SurveyResponse, Answer
from users.models import User


class Command(BaseCommand):
    help = 'Seed test surveys with responses'

    def handle(self, *args, **options):
        hr = User.objects.filter(is_hr=True).first()
        if not hr:
            self.stdout.write(self.style.ERROR('No HR user found'))
            return

        employees = list(User.objects.filter(is_hr=False))
        if not employees:
            self.stdout.write(self.style.ERROR('No employee users found'))
            return

        self._create_engagement_survey(hr, employees)
        self._create_nps_survey(hr, employees)
        self._create_anonymous_survey(hr, employees)

        self.stdout.write(self.style.SUCCESS('Test surveys created successfully'))

    def _create_engagement_survey(self, hr, employees):
        survey = Survey.objects.create(
            title='Оценка вовлечённости команды',
            description='Ежеквартальный опрос для оценки уровня вовлечённости сотрудников',
            status=Survey.STATUS_ACTIVE,
            is_anonymous=False,
            created_by=hr,
        )

        q1 = Question.objects.create(survey=survey, text='Как вы оцениваете атмосферу в команде?', question_type='single', order=0)
        for i, text in enumerate(['Отличная', 'Хорошая', 'Нейтральная', 'Напряжённая']):
            AnswerOption.objects.create(question=q1, text=text, order=i)

        q2 = Question.objects.create(survey=survey, text='Что мешает вашей работе? (можно выбрать несколько)', question_type='multiple', order=1)
        for i, text in enumerate(['Нехватка инструментов', 'Много совещаний', 'Неясные задачи', 'Шум в офисе', 'Ничего не мешает']):
            AnswerOption.objects.create(question=q2, text=text, order=i)

        q3 = Question.objects.create(survey=survey, text='Насколько вы удовлетворены своей ролью? (1 — совсем нет, 10 — полностью)', question_type='scale', order=2)

        q4 = Question.objects.create(survey=survey, text='Что бы вы улучшили в рабочих процессах?', question_type='text', order=3)

        opts1 = {o.text: o for o in q1.options.all()}
        opts2 = {o.text: o for o in q2.options.all()}

        responses_data = [
            ('Отличная', ['Много совещаний'], 8, 'Хотел бы меньше согласований'),
            ('Хорошая', ['Неясные задачи', 'Много совещаний'], 7, 'Улучшить документацию задач'),
            ('Хорошая', ['Ничего не мешает'], 9, ''),
            ('Нейтральная', ['Нехватка инструментов', 'Шум в офисе'], 5, 'Нормальные наушники и нормальные ноуты'),
            ('Отличная', ['Ничего не мешает'], 10, 'Всё устраивает'),
        ]

        for emp, (ans1, ans2_list, scale_val, text_val) in zip(employees, responses_data):
            resp = SurveyResponse.objects.create(survey=survey, user=emp)
            a1 = Answer.objects.create(response=resp, question=q1)
            a1.selected_options.set([opts1[ans1]])
            a2 = Answer.objects.create(response=resp, question=q2)
            a2.selected_options.set([opts2[t] for t in ans2_list if t in opts2])
            Answer.objects.create(response=resp, question=q3, text_answer=str(scale_val))
            if text_val:
                Answer.objects.create(response=resp, question=q4, text_answer=text_val)

        self.stdout.write(f'  Created: {survey.title}')

    def _create_nps_survey(self, hr, employees):
        survey = Survey.objects.create(
            title='NPS: готовность рекомендовать компанию',
            description='Насколько вероятно, что вы порекомендуете нашу компанию как место работы?',
            status=Survey.STATUS_ACTIVE,
            is_anonymous=False,
            created_by=hr,
        )

        q1 = Question.objects.create(survey=survey, text='Насколько вероятно, что вы порекомендуете компанию друзьям как место работы? (0–10)', question_type='nps', order=0)
        q2 = Question.objects.create(survey=survey, text='Как вы оцениваете уровень оплаты труда?', question_type='scale', order=1)
        q3 = Question.objects.create(survey=survey, text='Какой формат работы вы предпочитаете?', question_type='single', order=2)
        for i, text in enumerate(['Офис', 'Удалённо', 'Гибрид']):
            AnswerOption.objects.create(question=q3, text=text, order=i)

        opts3 = {o.text: o for o in q3.options.all()}

        nps_scores = [9, 8, 10, 3, 7]
        salary_scores = [7, 6, 8, 4, 7]
        formats = ['Гибрид', 'Удалённо', 'Гибрид', 'Офис', 'Удалённо']

        for emp, nps, sal, fmt in zip(employees, nps_scores, salary_scores, formats):
            resp = SurveyResponse.objects.create(survey=survey, user=emp)
            Answer.objects.create(response=resp, question=q1, text_answer=str(nps))
            Answer.objects.create(response=resp, question=q2, text_answer=str(sal))
            a3 = Answer.objects.create(response=resp, question=q3)
            a3.selected_options.set([opts3[fmt]])

        self.stdout.write(f'  Created: {survey.title}')

    def _create_anonymous_survey(self, hr, employees):
        survey = Survey.objects.create(
            title='Анонимная обратная связь по менеджменту',
            description='Анонимный опрос — ваши ответы не будут привязаны к вашему профилю',
            status=Survey.STATUS_ACTIVE,
            is_anonymous=True,
            created_by=hr,
        )

        q1 = Question.objects.create(survey=survey, text='Насколько вы доверяете руководству? (1–10)', question_type='scale', order=0)
        q2 = Question.objects.create(survey=survey, text='Что руководство делает хорошо?', question_type='multiple', order=1)
        for i, text in enumerate(['Ставит чёткие цели', 'Поддерживает команду', 'Прислушивается к мнению', 'Даёт обратную связь', 'Защищает интересы команды']):
            AnswerOption.objects.create(question=q2, text=text, order=i)
        q3 = Question.objects.create(survey=survey, text='Ваши пожелания руководству', question_type='text', order=2)

        opts2 = {o.text: o for o in q2.options.all()}

        trust_scores = [8, 6, 9, 5, 7]
        good_things = [
            ['Ставит чёткие цели', 'Поддерживает команду'],
            ['Прислушивается к мнению'],
            ['Ставит чёткие цели', 'Даёт обратную связь', 'Защищает интересы команды'],
            ['Поддерживает команду'],
            ['Ставит чёткие цели', 'Прислушивается к мнению'],
        ]
        wishes = [
            'Хотелось бы больше 1-on-1',
            'Чаще давать фидбэк по результатам',
            '',
            'Более прозрачно объяснять решения',
            'Меньше срочных задач в конце дня',
        ]

        for emp, score, good, wish in zip(employees, trust_scores, good_things, wishes):
            resp = SurveyResponse.objects.create(survey=survey, user=None)
            Answer.objects.create(response=resp, question=q1, text_answer=str(score))
            a2 = Answer.objects.create(response=resp, question=q2)
            a2.selected_options.set([opts2[t] for t in good if t in opts2])
            if wish:
                Answer.objects.create(response=resp, question=q3, text_answer=wish)

        self.stdout.write(f'  Created: {survey.title}')
