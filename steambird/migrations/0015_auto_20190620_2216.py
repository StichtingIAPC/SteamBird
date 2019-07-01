# Generated by Django 2.1.8 on 2019-06-20 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steambird', '0014_auto_20190620_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='period',
            field=models.CharField(choices=[('Q1', 'Quartile 1'), ('Q2', 'Quartile 2'), ('Q3', 'Quartile 3'), ('Q4', 'Quartile 4'), ('Q5', 'Quartile 5 (sad summer students)'), ('S1', 'Semester 1, half year course'), ('S2', 'Semester 2, half year course'), ('S3', 'Semester 3, half year course'), ('FULL_YEAR', 'Full year course')], max_length=32, verbose_name='The period in the year for this course'),
        ),
        migrations.AlterField(
            model_name='coursestudy',
            name='study_year',
            field=models.IntegerField(blank=True, choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')], null=True, verbose_name='The year of (nominal) study this course is given'),
        ),
    ]