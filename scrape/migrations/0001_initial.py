# Generated by Django 5.0.3 on 2024-04-20 08:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Kleinanzeigen',
            fields=[
                ('keyword_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scrape.keyword')),
                ('price', models.IntegerField(null=True)),
                ('distance', models.IntegerField()),
                ('latest_id', models.BigIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kleinanzeigen', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('scrape.keyword',),
        ),
        migrations.CreateModel(
            name='Urlaubspiraten',
            fields=[
                ('keyword_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='scrape.keyword')),
                ('latest_datetime', models.DateTimeField(default=None, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urlaubspiraten', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('scrape.keyword',),
        ),
    ]
