from django.shortcuts import render

from students.models import User

def student_detail(request, student_id):
    student = User.objects.get(id=student_id)
    # remember, the dictionary inside render is the variables that i want to pass into the html file
    return render(request, 'students/student_detail.html', {
        'student': student,
    })

