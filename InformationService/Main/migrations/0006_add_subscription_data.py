from django.db import migrations

def add_initial_subscriptions(apps, schema_editor):
    Subscription = apps.get_model('Main', 'Subscription')
    
    subscriptions = [
        {
            'name': 'Базовая',
            'description': 'Доступ к базовой библиотеке фильмов и сериалов в HD качестве. Просмотр на 1 устройстве.',
            'price': '299.00',
            'duration_days': 30
        },
        {
            'name': 'Стандарт',
            'description': 'Доступ ко всей библиотеке в Full HD качестве. Просмотр на 2 устройствах одновременно. Загрузка контента для офлайн просмотра.',
            'price': '499.00',
            'duration_days': 30
        },
        {
            'name': 'Премиум',
            'description': 'Полный доступ к библиотеке в 4K качестве. Просмотр на 4 устройствах одновременно. Эксклюзивный ранний доступ к новинкам. Загрузка контента для офлайн просмотра.',
            'price': '699.00',
            'duration_days': 30
        },
        {
            'name': 'Семейный',
            'description': 'Все преимущества Премиум подписки + возможность создания до 6 профилей. Просмотр на 6 устройствах одновременно. Родительский контроль.',
            'price': '899.00',
            'duration_days': 30
        },
        {
            'name': 'Студенческий',
            'description': 'Специальное предложение для студентов. Доступ к базовой библиотеке в HD качестве. Просмотр на 1 устройстве.',
            'price': '199.00',
            'duration_days': 30
        }
    ]
    
    for subscription_data in subscriptions:
        Subscription.objects.get_or_create(**subscription_data)

def remove_subscriptions(apps, schema_editor):
    Subscription = apps.get_model('Main', 'Subscription')
    Subscription.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('Main', '0005_alter_movie_options_movie_trailer_url_and_more'),
    ]

    operations = [
        migrations.RunPython(add_initial_subscriptions, remove_subscriptions),
    ] 