#!/bin/bash
# Activate virtual environment
source /home/ochogwuprince/alx-backend-graphql_crm/graphene/bin/activate

# Timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)

# Customers who have no orders in the past year
inactive_customers = Customer.objects.exclude(
    order_set__date__gte=one_year_ago  # replace 'order_set' with your related_name if different
).distinct()

count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log result
echo \"\$TIMESTAMP: Deleted \$DELETED_COUNT inactive customers\" >> /tmp/customer_cleanup_log.txt
