# Generated by Django 4.0.3 on 2022-05-07 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_alter_plangraf_activitykind_edudirect_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='facultybranch', to='schedule.branch', verbose_name='Филиал'),
        ),
    ]
