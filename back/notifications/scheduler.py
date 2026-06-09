import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)
_scheduler = None


def check_surveys():
    from surveys.models import Survey
    from .push import send_push_to_all

    now = timezone.now()
    print(f'[scheduler] check_surveys() at {now.strftime("%H:%M:%S")} UTC')

    # 1. Авто-активация: start_date наступил, опрос ещё черновик
    for survey in Survey.objects.filter(status='draft', start_date__lte=now):
        survey.status = 'active'
        survey.save(update_fields=['status'])
        logger.info('Auto-activated survey %s', survey.id)
        try:
            send_push_to_all(survey)
        except Exception as e:
            logger.warning('Push failed for survey %s: %s', survey.id, e)

    # 2. Напоминание: до end_date осталось <= PUSH_REMINDER_SECONDS_BEFORE_END
    reminder_seconds = getattr(settings, 'PUSH_REMINDER_SECONDS_BEFORE_END', 86400)
    threshold = now + timedelta(seconds=reminder_seconds)
    for survey in Survey.objects.filter(status='active', end_date__lte=threshold, reminder_sent=False):
        try:
            send_push_to_all(survey, reminder=True)
        except Exception as e:
            logger.warning('Reminder push failed for survey %s: %s', survey.id, e)
        survey.reminder_sent = True
        survey.save(update_fields=['reminder_sent'])
        logger.info('Sent reminder for survey %s', survey.id)

    # 3. Авто-завершение: end_date прошёл
    completed = Survey.objects.filter(status='active', end_date__lte=now).update(status='completed')
    if completed:
        logger.info('Auto-completed %d surveys', completed)


def start():
    global _scheduler
    if _scheduler is not None:
        return
    interval = getattr(settings, 'PUSH_SCHEDULER_INTERVAL_SECONDS', 60)
    _scheduler = BackgroundScheduler(timezone='UTC')
    _scheduler.add_job(check_surveys, 'interval', seconds=interval, id='check_surveys')
    _scheduler.start()
    print(f'[scheduler] started, interval={interval}s')
    logger.info('Push scheduler started, interval=%ds', interval)
