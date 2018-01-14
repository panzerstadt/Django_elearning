from django.db import models
from django.urls import reverse
from django.conf import settings

from students.models import User

# when we run manage.py makemigrations, django looks here and creates new models (1 model = 1 table in database)
# and prepares them for adding into the database

# when changing how the model works, we need to 'makemigrations' and then 'migrate' the updated model

# in the database, you can see that the naming follows the convention 'appName_modelName'
# app is called 'elearning'
# the first model(read: database) is called 'courses'. the other one is called 'students'
# in here, the 'courses' model uses a class Course to represent the model
class Course(models.Model):
    name = models.CharField(max_length=200)
    students = models.ManyToManyField(User)

    def get_absolute_url(self):
        return reverse('course_detail', args=(self.id, ))

    # this is where the label for the course name on the admin page is
    # if you return name (from within the class) here then it will be reflected in the course admin page
    def __str__(self):
        return self.name


class Section(models.Model):
    # OneToMany relationships are modelled as ForeignKey in Django
    # ForeignKey is used on the 'Many' side of the relationship in OneToMany
    # so in here, the 'course' variable relies on ForeignKeys from 'Course'.
    # therefore 'Section' doesn't exist without 'Course', which makes sense
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    # name of course, title of section (no reason other than convention)
    title = models.CharField(max_length=100)
    # number is used to order the course titles
    number = models.IntegerField()
    # text variable is section content. this is where the elearning content is
    text = models.TextField()

    class Meta:
        # unique_together is a django magic that makes sure
        # each number can only occur once in the course
        unique_together = ('course', 'number', )

    def __str__(self):
        return self.text

    def get_test_url(self):
        return reverse('do_test', args=(self.id,))

    def get_absolute_url(self):
        return reverse('do_section', args=(self.id,))

    def get_next_section_url(self):
        next_section = Section.objects.get(number=self.number+1)
        return reverse('do_section', args=(next_section.id,))


class Question(models.Model):
    # takes stuff from section, because
    # each question can only belong to one section
    # OneToMany
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.text


class Answer(models.Model):
    answer = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    text = models.CharField(max_length=1000)
    correct = models.BooleanField()

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    answer = models.ForeignKey(Answer, on_delete=models.DO_NOTHING)
    # because we are not sure which model implements the user model
    # we use the settings.AUTH_USER_MODEL to point to the right model.
    # django automatically finds the right model to grab the user from.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    class Meta:
        # each user can only have one answer for each question
        unique_together = ('question', 'user', )
