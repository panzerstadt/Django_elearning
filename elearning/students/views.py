from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from students.models import User
from courses.models import Course
from courses.views import calculate_score

def get_all_scores_for_user(user):
    scores = []
    for course in Course.objects.all():
        course_scores = []
        for section in course.section_set.order_by('number'):
            course_scores.append((section, calculate_score(user, section),))
        scores.append((course, course_scores),)
    return scores

def unsafe_student_detail(request, student_id):
    # because student_id is fed through url, you can just input a number and if the id matches
    # the student details are shown (which is a big privacy problem)
    student = User.objects.get(id=student_id)
    # remember, the dictionary inside render is the variables that i want to pass into the html file
    return render(request, 'students/student_detail.html', {
        'student': student,
    })

def student_detail(request):
    # is_authenticated() with brackets =  < django 2.0
    # is_authenticated without brackets = > django 2.0
    if not request.user.is_authenticated:
        raise PermissionDenied
    # this query for request.user is trustable because
    # if the user is not logged in, it doesn't exist
    student = request.user
    return render(request, 'students/student_detail.html', {
        'student': student,
        'scores': get_all_scores_for_user(student),
    })
