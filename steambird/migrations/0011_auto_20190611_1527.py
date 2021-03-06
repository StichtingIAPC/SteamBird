# Generated by Django 2.1.8 on 2019-06-11 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steambird', '0010_auto_20190608_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursestudy',
            name='study_year',
            field=models.IntegerField(blank=True, choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')], null=True, verbose_name='The year of (nominal) study this course is given'),
        ),
    ]
