# Generated by Django 3.1.5 on 2021-04-02 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_auto_20210402_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='cet6_grades',
            field=models.FloatField(blank=True, null=True, verbose_name='CET6成绩'),
        ),
    ]
