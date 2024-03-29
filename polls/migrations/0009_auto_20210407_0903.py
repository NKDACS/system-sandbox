# Generated by Django 3.1.6 on 2021-04-07 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_auto_20210407_0850'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='addition',
            field=models.TextField(blank=True, max_length=1024, verbose_name='其他补充说明'),
        ),
        migrations.AlterField(
            model_name='resume',
            name='cet6_grades',
            field=models.FloatField(blank=True, null=True, verbose_name='CET6成绩(未通过填0)'),
        ),
    ]
