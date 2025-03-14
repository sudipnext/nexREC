# Generated by Django 5.1.6 on 2025-03-04 11:07

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_delete_userembeddings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEmbeddings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embeddings', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), null=True, size=384)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('interaction_count', models.IntegerField(default=0)),
                ('version', models.CharField(default='1.0', max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='embeddings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'User embeddings',
                'indexes': [models.Index(fields=['last_updated'], name='core_userem_last_up_629f02_idx'), models.Index(fields=['user', 'last_updated'], name='core_userem_user_id_1cff5a_idx')],
            },
        ),
    ]
