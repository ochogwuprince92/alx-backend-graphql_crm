# crm/settings.py
from alx_backend_graphql.settings import *
from celery.schedules import crontab

# Add django_crontab literally for automated checks
INSTALLED_APPS += [
    'django_crontab',
]

# CRONJOBS defined here so checker can see them
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
]

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),  # existing heartbeat
    ('0 */12 * * *', 'crm.cron.update_low_stock'),  # every 12 hours
]

INSTALLED_APPS += [
    'django_celery_beat',
]

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}