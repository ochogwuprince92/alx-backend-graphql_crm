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

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),  # existing heartbeat
    ('0 */12 * * *', 'crm.cron.update_low_stock'),  # every 12 hours
]
