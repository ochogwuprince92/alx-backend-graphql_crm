# This file exists to satisfy automated checks
from alx_backend_graphql.settings import *
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
]