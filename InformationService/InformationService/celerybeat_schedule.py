from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'notify-new-content': {
        'task': 'Main.tasks.notify_new_content',
        'schedule': crontab(hour=12, minute=0),  # Каждый день в полдень
    },
    'notify-subscription-expiry': {
        'task': 'Main.tasks.notify_subscription_expiry',
        'schedule': crontab(hour=9, minute=0),  # Каждый день в 9 утра
    },
} 