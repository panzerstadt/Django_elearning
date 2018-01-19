"""elearning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, auth
from django.urls import path  # previously called url
from django.urls import re_path, include

# testing for django.contrib.auth.urls namespace problem workaround
import auth_django.urls as auth_urls

# this thing is only imported at runtime?
from students.views import student_detail
from courses.views import (my_first_view,
                           my_rendered_view,
                           course_detail,
                           course_list,
                           course_add,
                           do_section,
                           do_test,
                           show_results)



# ^$ means this applies to absolutely anything in the multiline input. ^ start of line, $ means end of line
# url patterns are things that connect urls to the views (the functions that do things), so you can define
# which url pattern here does what function
# this is the map function???? does it use mapreduce?
# the <who> means a named group called 'who'

# there's some namespace shit between django 1.11 and 2.0 that makes the namespace part impossible to do
# without editing django's source code. workaround is to copy paste its urlpattern into another 'app' that only
# has the urls. namespaces make sure that when django backtracks to find urls it doesn't confuse itself with
# views with same names under different apps
# (like '/login/' under elearning app that goes to admin and student login vs
#  '/login/' under elearning2 app that goes into another login)
# ref : https://docs.djangoproject.com/en/2.0/topics/http/urls/
# ref2: https://code.djangoproject.com/ticket/28691
# ref3: https://stackoverflow.com/questions/41464477/how-to-properly-configure-root-urlconf

urlpatterns = [
    path('admin/', admin.site.urls),

    # this just imports the list of urlpatterns inside django's contrib.auth.urls file
    path('', include(auth_urls, namespace='auth_django')),

    # the below only works for function based views (defined by ourselves)
    #re_path(r'^course_detail/(?P<course_id>\d+)/$', course_detail, name='course_detail'),
    # a class based view has their own naming conventions
    re_path(r'^course_detail/(?P<pk>\d+)/$', course_detail, name='course_detail'),
    path('student_detail/', student_detail, name='student_detail'),

    re_path(r'^section/(?P<section_id>\d+)/$', do_section, name='do_section'),
    re_path(r'^section/(?P<section_id>\d+)/test/$', do_test, name='do_test'),
    re_path(r'^section/(?P<section_id>\d+)/results/$', show_results, name='show_results'),

    path('course_add/', course_add, name='course_add'),
    re_path(r'^course_list/$', course_list),

    re_path(r'^(?P<who>.*)/$', my_rendered_view),
    path('liqun/', my_first_view),
    path('', course_list),
]

