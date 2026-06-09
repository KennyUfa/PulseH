from django.apps import AppConfig

_SKIP_CMDS = {'migrate', 'makemigrations', 'shell', 'collectstatic',
              'createsuperuser', 'seed_demo', 'check', 'showmigrations'}


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        import sys
        import os

        argv = sys.argv
        # Пропускаем команды которым планировщик не нужен
        if len(argv) > 1 and argv[1] in _SKIP_CMDS:
            return

        # При runserver запускаем только в основном процессе (не в file watcher)
        if argv[0].endswith('manage.py') and os.environ.get('RUN_MAIN') != 'true':
            return

        from .scheduler import start
        start()
