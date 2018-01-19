from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db import transaction
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.urls import reverse

# to use class based views import these
"""
Django also has generic views to make it super easy to make views without having to repeat stuff
they exist as class views.
"""
from django.views.generic import DetailView, CreateView, ListView


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

# function based view
# if using class based view, course and return render uses a default template
# (which is what is used for the current function below)
# def course_detail(request, course_id):
#     course = Course.objects.get(id=course_id)
#     return render(request, 'courses/course_detail.html', {
#         'course': course,
#     })

# class based view
class CourseDetailView(DetailView):
    # this class, when turned into a view,
    # has the default return as (current folder, name of variable that you tie your class to)

    # the only thing you really need to get class based views to work is to
    # point it to the model in use (like below)
    model = Course

# this is how you turn a class into a view method
# you call the .as_view() to turn the class into a view. not all classes obviously
# this turns 'course_detail' into a view function
course_detail = CourseDetailView.as_view()

# same here
# def course_list(request):
#     # the below is inefficient apparently
#     #courses = Course.objects.all()
#     # so we use one of two: prefetch_related() or select_related() function
#     # select_related() for OneToMany
#     # prefetch_related() for ManyToMany, and ManyToOne(the 'Many' end of the OneToMany relationship)
#     courses = Course.objects.prefetch_related('students')
#     # it performs one database query per related model
#     return render(request, 'courses/course_list.html', {
#         'courses':courses,
#     })

class CourseListView(ListView):
    model = Course
    # this is also a performance enhancement option used in the function based view
    # othersie it will default to Course.objects.all(), where Course is the model
    # you're accessing (model = database)
    queryset = Course.objects.prefetch_related('students')

course_list = CourseListView.as_view()

# 2 lines in class based views vs 10.
# but function based views are more debuggable
# to debug class based views, you usually have to go into
# the superclasses to fix stuff O_O
# def course_add(request):
#     if request.POST:
#         form = CourseForm(request.POST)
#         if form.is_valid():
#             new_course = form.save()
#             return HttpResponseRedirect(new_course.get_absolute_url())
#     else:
#         form = CourseForm()
#         return render(request, 'courses/course_form.html', {
#             'form': form,
#         })

class CourseAddView(CreateView):
    model = Course
    # in create view, this is required
    # this specifies the list of views that the class should accept
    # TODO: NOT RECOMMENDED IN REAL WORLD APPLICATIONS, BECAUSE
    # TODO: IF YOU WRITE NEW FIELDS THAT SHOULD NOT BE WRITEABLE
    # TODO: BY A USER AND YOU DON'T CHANGE THIS,
    # TODO: THERE WILL BE A SECURITY ISSUE
    fields = '__all__'

course_add = CourseAddView.as_view()

def do_section(request, section_id):
    section = Section.objects.get(id=section_id)
    return render(request, 'courses/do_section.html', {
        'section': section,
    })

# this is damn hard to turn into a class based view
# and there is no benefit because it is quite specific to this use case
# and doing it as a class based view does not shorten the code substantially, while
# debugging it would be harder (superclass is in another file)
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