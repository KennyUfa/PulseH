import json
import logging
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)


def _time_left(end_date):
    if not end_date:
        return ''
    now = datetime.now(dt_timezone.utc)
    diff = end_date - now
    seconds = int(diff.total_seconds())
    if seconds <= 0:
        return 'истёк'
    if seconds < 3600:
        minutes = seconds // 60
        return f'~{minutes} мин.'
    if seconds < 86400:
        hours = seconds // 3600
        return f'~{hours} ч.'
    days = seconds // 86400
    return f'{days} дн.'


def send_push(subscription, title, body, url, survey_id):
    data = json.dumps({'title': title, 'body': body, 'url': url, 'survey_id': survey_id})
    try:
        webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {'p256dh': subscription.p256dh, 'auth': subscription.auth},
            },
            data=data,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={'sub': f'mailto:{settings.VAPID_CLAIM_EMAIL}'},
            timeout=10,
        )
    except WebPushException as e:
        status = getattr(e.response, 'status_code', None) if getattr(e, 'response', None) else None
        msg = str(e).lower()
        if status in (404, 410) or '410' in msg or '404' in msg or 'gone' in msg or 'unsubscribed' in msg or 'expired' in msg:
            subscription.delete()
            logger.info('Removed dead push subscription %s', subscription.endpoint[:60])
        else:
            logger.warning('WebPush failed for %s: %s', subscription.endpoint[:60], e)
    except Exception as e:
        logger.warning('Push send error: %s: %s', type(e).__name__, e)


def send_push_to_all(survey, reminder=False):
    from .models import PushSubscription

    if reminder:
        title = f'Напоминание: «{survey.title}»'
        time_str = _time_left(survey.end_date)
        body = f'Осталось {time_str} — успейте пройти опрос!'
    else:
        title = f'Новый опрос: «{survey.title}»'
        time_str = _time_left(survey.end_date)
        body = f'До окончания — {time_str}.' if time_str else 'Пройдите опрос прямо сейчас.'

    url = f'/surveys/{survey.id}'

    from surveys.models import SurveyResponse
    responded_ids = SurveyResponse.objects.filter(survey=survey).values_list('user_id', flat=True)

    subs = PushSubscription.objects.select_related('user').filter(
        user__is_active=True,
    ).exclude(user_id__in=responded_ids)

    for sub in subs:
        send_push(sub, title, body, url, survey.id)
