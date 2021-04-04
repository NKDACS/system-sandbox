# Generated by Django 3.1.5 on 2021-04-02 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='major_choices',
            field=models.CharField(blank=True, choices=[(0, '统计学'), (1, '应用统计')], max_length=16, verbose_name='报名专业'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='cet6',
            field=models.BooleanField(default=False, verbose_name='是否通过cet6'),
        ),
    ]
