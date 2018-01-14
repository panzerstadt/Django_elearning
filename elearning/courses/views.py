from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import transaction
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import reverse


from courses.models import Course, Section, Question, UserAnswer
from courses.forms import CourseForm

# a django view is a thing that processes your requests
# django view : take things, do things, customer facing (app user)

# takes the request argument and returns a string
def my_first_view(request, who):
    return HttpResponse("Hello {0}!" .format(who))

# render(request, template)
# renders templates (as in, html files with the correct format)
# you can also pass arguments from the url straight into the template by using template contexts
def my_rendered_view(request, who):
    return render(request=request, template_name='courses/hello.html', context={
        'who': who,
    })

def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    return render(request, 'courses/course_detail.html', {
        'course': course,
    })

def course_list(request):
    # the below is inefficient apparently
    #courses = Course.objects.all()
    # so we use one of two: prefetch_related() or select_related() function
    # select_related() for OneToMany
    # prefetch_related() for ManyToMany, and ManyToOne(the 'Many' end of the OneToMany relationship)
    courses = Course.objects.prefetch_related('students')
    # it performs one database query per related model
    return render(request, 'courses/course_list.html', {
        'courses':courses,
    })

def course_add(request):
    if request.POST:
        form = CourseForm(request.POST)
        if form.is_valid():
            new_course = form.save()
            return HttpResponseRedirect(new_course.get_absolute_url())
    else:
        form = CourseForm()
        return render(request, 'courses/course_form.html', {
            'form': form,
        })

def do_section(request, section_id):
    section = Section.objects.get(id=section_id)
    return render(request, 'courses/do_section.html', {
        'section': section,
    })

def do_test(request, section_id):
    # check if the user is logged in, reject, which will result in a http error 403
    if not request.user.is_authenticated:
        raise PermissionDenied

    # get the section from the database, taken from the url
    # and perform a DB query to get the database section object
    section = Section.objects.get(id=section_id)
    if request.method == 'POST':
        # in case something goes wrong inside the 'with' statement, nothing in the database
        # is altered (if shit happens rollback)
        with transaction.atomic():
            # find user's section from models.section (sections in a course)
            # and delete the section
            # deletes all UserAnswers that the user has posted before
            # this allows the user to take the test multiple times
            UserAnswer.objects.filter(user=request.user,
                                      question__section=section).delete()
            # not the usual way of doing things. usually uses a django form to
            # process the POST request
            # usually a Django form is much easier as it's an API, this below
            # is technically reinventing the wheel
            for key, value in request.POST.items():
                # django's default security feature
                # if the key is this thing, skip the loop.
                # this token is part of the POST request due to an implemented
                # django security feature
                if key == 'csrfmiddlewaretoken':
                    continue

                # get question
                # what the data looks like: {'question-1' : '2'}
                # get the question number (1 in the eg above) and get the question object
                question_id = key.split('-')[1]
                question = Question.objects.get(id=question_id)

                # get user's answer
                answer_id = int(request.POST.get(key))  # link the security key to the answer_id
                if answer_id not in question.answer_set.values_list('id', flat=True):
                    # this exception is in a http 400 response
                    raise SuspiciousOperation('Answer is not valid for the question')
                user_answer = UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    answer_id=answer_id,
                )

        return redirect(reverse('show_results', args=(section_id,)))
    return render(request, 'courses/do_test.html', {
        'section': section
    })

def calculate_score(user, section):
    questions = Question.objects.filter(section=section)
    correct_answers = UserAnswer.objects.filter(
        user=user,
        question__section=section,
        answer__correct=True
    )
    try:
        return (correct_answers.count() / questions.count()) * 100
    except:
        return 'not taken'

def show_results(request, section_id):
    if not request.user.is_authenticated:
        raise PermissionDenied
    section = Section.objects.get(id=section_id)
    return render(request, 'courses/show_results.html', {
        'section': section,
        'score': calculate_score(request.user, section)
    })