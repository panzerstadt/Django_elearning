from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from students.models import User
from courses.models import Section
from courses.views import perform_test, calculate_score
from api.serializers import UserSerializer, SectionSerializer  # this is something you define yourself

from django.core.exceptions import PermissionDenied

# django rest framework provides even more stuff than class based view templates
# they are called viewsets
# viewsets define several views that are all under one common task

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('-date_joined')
    serializer_class = UserSerializer

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    """
    the following functions (functions in a viewset)
    defines views (thing-doers) all together that can be accessed through /sections/
    because 'sections' has been registered in url.py under router.register(r'sections', SectionViewSet)
    this connects the class SectionViewset (this class) directly to /api/sections
    because /api/ is registered in the urlpattern as the django-rest-framework version of views
    """

    # using detail route we can declare which endpoints this function supports
    # to block POST or PUT, because you haven't designed the function for that
    # and it might lead to app breaking bugs
    @detail_route(methods=['GET', ])
    def questions(self, request, *args, **kwargs):
        # we want the endpoint to return a list of questions
        section = self.get_object()
        data = []
        # for the list of questions in the section...
        for question in section.question_set.all():
            question_data = {'id': question.id, 'question': question.text, 'answers': []}
            # append all answers to that question
            for answer in question.answer_set.all():
                answer_data = {'id': answer.id, 'text': str(answer), }
                question_data['answers'].append(answer_data)
            data.append(question_data)
        return Response(data)

    @detail_route(methods=['PUT', ])
    def test(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        section = self.get_object()  # not too sure where this thing gets its objects
        perform_test(request.user, request.data, section)
        # if everything is ok, return an empty response
        return Response()

    @detail_route(methods=['GET', ])
    def result(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        # make my own json (which is a dictionary)
        return Response({
            'score': calculate_score(request.user, self.get_object())
        })