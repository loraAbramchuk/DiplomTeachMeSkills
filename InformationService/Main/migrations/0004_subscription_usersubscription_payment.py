# Generated by Django 4.2.20 on 2025-04-22 10:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Main', '0003_review_serial_alter_review_movie'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('duration_days', models.IntegerField(verbose_name='Длительность (в днях)')),
            ],
            options={
                'verbose_name': 'Подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.CreateModel(
            name='UserSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата начала')),
                ('end_date', models.DateTimeField(verbose_name='Дата окончания')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('auto_renewal', models.BooleanField(default=True, verbose_name='Автопродление')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Main.subscription', verbose_name='Тип подписки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка пользователя',
                'verbose_name_plural': 'Подписки пользователей',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Сумма')),
                ('payment_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата платежа')),
                ('status', models.CharField(choices=[('pending', 'В обработке'), ('completed', 'Выполнен'), ('failed', 'Ошибка'), ('refunded', 'Возвращен')], default='pending', max_length=20, verbose_name='Статус')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Main.subscription', verbose_name='Тип подписки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Платеж',
                'verbose_name_plural': 'Платежи',
            },
        ),
    ]
