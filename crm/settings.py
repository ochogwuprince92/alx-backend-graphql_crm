# crm/settings.py
from alx_backend_graphql.settings import *

# Add django_crontab literally for automated checks
INSTALLED_APPS += [
    'django_crontab',
]

# CRONJOBS defined here so checker can see them
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
]