from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from surveys.models import Survey, Question, AnswerOption


# condition_question_index — индекс вопроса-условия в этом же списке
# condition_option_text   — текст варианта, при котором вопрос показывается
QUESTIONS = [
    # 0
    {
        'text': 'Какой главный приз за хакатон?',
        'question_type': 'single',
        'options': ['Айфон', 'Клавиатура', '2 пива и беляш'],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 1 — показывается только если выбрали «Айфон»
    {
        'text': 'Какой именно айфон?',
        'question_type': 'single',
        'options': ['17', '17 про', '17 про макс'],
        'condition_question_index': 0,
        'condition_option_text': 'Айфон',
    },
    # 2
    {
        'text': 'Какой главный критерий оценки?',
        'question_type': 'single',
        'options': ['Визуал', 'Функционал', 'Лишь бы работало'],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 3
    {
        'text': 'Если у тебя есть два стула: один – очень удобный, но греет попу, а второй – абсолютно нормальный, но время от времени слегка подпрыгивает, на какой сядешь?',
        'question_type': 'single',
        'options': [
            'На греющий, потому что зимой полезно!',
            'На прыгающий, мне и так в тренажерке скучно.',
            'Поставлю их рядом, буду перекатываться туда-сюда – тренировка баланса!',
            'Сяду на пол между ними – я легенда, а не стул.',
            'Попробую оба, потом напишу отзыв на Яндекс.Маркете.',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 4
    {
        'text': 'Если бы ты мог на один день превратиться в домашнее животное, кем бы выбрал быть?',
        'question_type': 'single',
        'options': [
            'Котом, чтобы весь день валяться и получать уважение за лень.',
            'Псом, чтобы получать поглаживания и вкусняшки без необходимости лаять на прохожих.',
            'Хомяком, просто ради важной миссии – контроль за всеми шариками в мире.',
            'Рыбкой, чтобы никто не спрашивал, почему ты не убираешься.',
            'Я бы остался собой, но с кошачьими ушками – компромисс!',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 5
    {
        'text': 'Если бы утром тебе давали один бесплатный кофе или один вечером бесплатный чай, что бы выбрал?',
        'question_type': 'single',
        'options': [
            'Кофе утром, потому что без него я – зомби, а не человек.',
            'Чай вечером, потому что мне нужна расслабуха, а не турбо-режим.',
            'Оба, я экономный и неунывающий трудяга.',
            'Ни кофе, ни чай – я пью воду и шепчу: «я молодец».',
            'Дайте мне кофе вечером, я революционер, который спит в 5 утра.',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 6
    {
        'text': 'Если бы можно было работать видеокамерой, офисной ручкой или календарем, кем бы ты выбрал быть?',
        'question_type': 'single',
        'options': [
            'Камерой – смотрю, как все работают, и мало что делаю сам.',
            'Ручкой – пишу важные документы, но часто теряюсь.',
            'Календарем – напоминаю о дедлайнах, но всех ненавидят.',
            'Кофеваркой – главный герой офиса.',
            'Я бы остался человеком, но только по вторникам.',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 7 — multiple
    {
        'text': 'Если бы у тебя была суперсила, но только для повседневных дел, какая бы это была сила? (можно выбрать несколько)',
        'question_type': 'multiple',
        'options': [
            'Телепортация в магазин – без пробок и обуви.',
            'Ускоренное приготовление еды – готовлю, как Шрек.',
            'Чтение мыслей, но только о том, где лежат ключи.',
            'Мгновенно убираться – щелчок, и порядок.',
            'Невидимость... чтобы не здороваться с соседями.',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 8
    {
        'text': 'Если бы пицца, суши и борщ устроили турнир по поеданию людей, за кого бы ты болел?',
        'question_type': 'single',
        'options': [
            'За пиццу – она горячая и хрустящая, как справедливость.',
            'За суши – холодные, но смертельно опасные.',
            'За борщ – традиционный и стабильный, как бабушка.',
            'Я не ем побеждённых – буду болеть за салат «Оливье».',
            'Я миролюбивый, я бы их всех угостил чаем.',
        ],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 9
    {
        'text': 'У меня жена хочет айфон и есть 2 ребёнка, которые хотят велосипеды. Вы пришлёте мне оффер?',
        'question_type': 'single',
        'options': ['Да конечно!', 'Подумаем'],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 10 — scale
    {
        'text': 'Оцени уровень своей готовности к работе прямо сейчас (1 — сплю сидя, 10 — могу горы свернуть)',
        'question_type': 'scale',
        'options': [],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 11 — nps
    {
        'text': 'Насколько вероятно, что ты порекомендуешь наш офис своему другу как место работы?',
        'question_type': 'nps',
        'options': [],
        'condition_question_index': None,
        'condition_option_text': '',
    },
    # 12 — text
    {
        'text': 'Есть что добавить, пожаловаться или похвалить? Пиши сюда — всё анонимно:',
        'question_type': 'text',
        'options': [],
        'condition_question_index': None,
        'condition_option_text': '',
    },
]


class Command(BaseCommand):
    help = 'Создаёт два демо-опроса (анонимный и именной) со стартом через 1 минуту'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        for is_anonymous in (True, False):
            title = (
                'Хакатон: пятничный опрос (анонимный)'
                if is_anonymous else
                'Хакатон: пятничный опрос'
            )
            survey = Survey.objects.create(
                title=title,
                description='Опрос для поднятия настроения и изучения команды. Без правильных ответов — только честные.',
                is_anonymous=is_anonymous,
                status='draft',
                start_date=now + timedelta(seconds=60),
                end_date=now + timedelta(hours=24),
            )
            for order, q_data in enumerate(QUESTIONS):
                question = Question.objects.create(
                    survey=survey,
                    text=q_data['text'],
                    question_type=q_data['question_type'],
                    order=order,
                    condition_question_index=q_data['condition_question_index'],
                    condition_option_text=q_data['condition_option_text'],
                )
                for opt_order, opt_text in enumerate(q_data['options']):
                    AnswerOption.objects.create(
                        question=question,
                        text=opt_text,
                        order=opt_order,
                    )
            self.stdout.write(self.style.SUCCESS(
                f'✓ id={survey.id} | {"анонимный" if is_anonymous else "именной  "} | '
                f'старт {survey.start_date.strftime("%H:%M:%S")} UTC | '
                f'{len(QUESTIONS)} вопросов'
            ))
