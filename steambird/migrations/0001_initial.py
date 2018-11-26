# Generated by Django 2.1.3 on 2018-11-26 23:04

from django.db import migrations, models
import django.db.models.deletion
import steambird.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.IntegerField(unique=True, verbose_name='Course code of module, references Osiris')),
                ('name', models.CharField(max_length=50, verbose_name='Name of Course')),
                ('year', models.IntegerField()),
                ('updated_teacher', models.BooleanField(default=False, verbose_name='Has the course been marked updated by the teacher for this year?')),
                ('updated_IAPC', models.BooleanField(default=False, verbose_name='Have we already checked this course this year?')),
            ],
        ),
        migrations.CreateModel(
            name='MaterialSelectionProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255, null=True, verbose_name='Reason why there is a difference between Osiris and availability')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Name of module')),
                ('course_code', models.IntegerField(unique=True, verbose_name='Course code of module, references Osiris')),
                ('module_moment', models.CharField(choices=[(steambird.models.ModuleMoment('Year one, Quartile 1'), 'Year one, Quartile 1'), (steambird.models.ModuleMoment('Year one, Quartile 2'), 'Year one, Quartile 2'), (steambird.models.ModuleMoment('Year one, Quartile 3'), 'Year one, Quartile 3'), (steambird.models.ModuleMoment('Year one, Quartile 4'), 'Year one, Quartile 4'), (steambird.models.ModuleMoment('Year two, Quartile 1'), 'Year two, Quartile 1'), (steambird.models.ModuleMoment('Year two, Quartile 2'), 'Year two, Quartile 2'), (steambird.models.ModuleMoment('Year two, Quartile 3'), 'Year two, Quartile 3'), (steambird.models.ModuleMoment('Year two, Quartile 4'), 'Year two, Quartile 4'), (steambird.models.ModuleMoment('Year three, Quartile 1'), 'Year three, Quartile 1'), (steambird.models.ModuleMoment('Year three, Quartile 2'), 'Year three, Quartile 2'), (steambird.models.ModuleMoment('Year three, Quartile 3'), 'Year three, Quartile 3'), (steambird.models.ModuleMoment('Year three, Quartile 4'), 'Year three, Quartile 4')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name of the study, e.g. Creative Technology')),
                ('study_type', models.CharField(choices=[(steambird.models.StudyType('Bachelor'), 'Bachelor'), (steambird.models.StudyType('Master'), 'Master'), (steambird.models.StudyType('PreMaster'), 'PreMaster')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='StudyCourse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(choices=[(steambird.models.Period('Quartile 1'), 'Quartile 1'), (steambird.models.Period('Quartile 2'), 'Quartile 2'), (steambird.models.Period('Quartile 3'), 'Quartile 3'), (steambird.models.Period('Quartile 4'), 'Quartile 4'), (steambird.models.Period('Quartile 5 (sad summer students)'), 'Quartile 5 (sad summer students)'), (steambird.models.Period('Quartile 1, half year course'), 'Quartile 1, half year course'), (steambird.models.Period('Quartile 3, half year course'), 'Quartile 3, half year course'), (steambird.models.Period('Full year course'), 'Full year course')], max_length=10)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='steambird.Course')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='steambird.Study')),
            ],
        ),
        migrations.CreateModel(
            name='StudyMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='StudyMaterialEdition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titles', models.CharField(max_length=50)),
                ('initials', models.CharField(max_length=15)),
                ('first_name', models.CharField(max_length=50)),
                ('surname_prefix', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True, verbose_name='Is the teacher still active at the UT?')),
                ('retired', models.BooleanField(default=False, verbose_name='Is the teacher retried?')),
                ('last_login', models.DateTimeField(verbose_name='Last Login')),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('studymaterialedition_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='steambird.StudyMaterialEdition')),
                ('ISBN', models.CharField(max_length=13, unique=True, verbose_name='ISBN 13, used if book is from after 2007')),
                ('author', models.CharField(max_length=1000, verbose_name='Author names, these should be added automatically based on the ISBN search')),
                ('img', models.URLField()),
                ('year_of_publishing', models.IntegerField(max_length=4)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('steambird.studymaterialedition',),
        ),
        migrations.CreateModel(
            name='OtherMaterial',
            fields=[
                ('studymaterialedition_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='steambird.StudyMaterialEdition')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('steambird.studymaterialedition',),
        ),
        migrations.CreateModel(
            name='ScientificArticle',
            fields=[
                ('studymaterialedition_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='steambird.StudyMaterialEdition')),
                ('DOI', models.CharField(blank=True, max_length=255, verbose_name="Digital Object Identifier used for most Scientific Articles. Unique per article, if it has one (conference proceedings don't tend to have one)")),
                ('author', models.CharField(max_length=1000, verbose_name='Author names, these should be added automatically based on the DOI search')),
                ('year_of_publishing', models.IntegerField(max_length=4)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('steambird.studymaterialedition',),
        ),
        migrations.AddField(
            model_name='studymaterialedition',
            name='material_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='steambird.StudyMaterial'),
        ),
        migrations.AddField(
            model_name='studymaterialedition',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_steambird.studymaterialedition_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='study',
            name='courses',
            field=models.ManyToManyField(through='steambird.StudyCourse', to='steambird.Course'),
        ),
        migrations.AddField(
            model_name='module',
            name='coordinator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='steambird.Teacher', verbose_name='Coordinator reference for a module, references the Teacher'),
        ),
        migrations.AddField(
            model_name='materialselectionprocess',
            name='approved_material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='process_is_approved', to='steambird.StudyMaterialEdition'),
        ),
        migrations.AddField(
            model_name='materialselectionprocess',
            name='available_materials',
            field=models.ManyToManyField(related_name='process_is_available', to='steambird.StudyMaterialEdition'),
        ),
        migrations.AddField(
            model_name='materialselectionprocess',
            name='osiris_specified_material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='process_in_osiris', to='steambird.StudyMaterialEdition'),
        ),
        migrations.AddField(
            model_name='course',
            name='materials',
            field=models.ManyToManyField(to='steambird.MaterialSelectionProcess'),
        ),
        migrations.AddField(
            model_name='course',
            name='module',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='steambird.Module', verbose_name='Links course to possible module (maths) if needed'),
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ManyToManyField(to='steambird.Teacher'),
        ),
        migrations.AlterUniqueTogether(
            name='studycourse',
            unique_together={('course', 'study')},
        ),
        migrations.AlterUniqueTogether(
            name='course',
            unique_together={('course_code', 'year')},
        ),
    ]
