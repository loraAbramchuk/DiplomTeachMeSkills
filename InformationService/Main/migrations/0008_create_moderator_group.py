from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_moderator_group(apps, schema_editor):
    # Создаем группу модераторов
    moderator_group, created = Group.objects.get_or_create(name='Модераторы')
    
    # Получаем типы контента для наших моделей
    movie_content_type = ContentType.objects.get(app_label='Main', model='movie')
    serial_content_type = ContentType.objects.get(app_label='Main', model='serial')
    review_content_type = ContentType.objects.get(app_label='Main', model='review')
    
    # Права для фильмов
    movie_permissions = Permission.objects.filter(
        content_type=movie_content_type,
        codename__in=['add_movie', 'change_movie', 'delete_movie']
    )
    
    # Права для сериалов
    serial_permissions = Permission.objects.filter(
        content_type=serial_content_type,
        codename__in=['add_serial', 'change_serial', 'delete_serial']
    )
    
    # Права для отзывов (только изменение и удаление)
    review_permissions = Permission.objects.filter(
        content_type=review_content_type,
        codename__in=['change_review', 'delete_review']
    )
    
    # Добавляем все права группе модераторов
    moderator_group.permissions.add(
        *movie_permissions,
        *serial_permissions,
        *review_permissions
    )

def remove_moderator_group(apps, schema_editor):
    Group.objects.filter(name='Модераторы').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('Main', '0007_alter_country_options_alter_genre_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_moderator_group, remove_moderator_group),
    ] 