from rest_framework import serializers

# serializer's purpose is to serialize and de-serialize data
# meaning convert
# typically serializers output json. but they can output anything

# Serializer object for students app

from students.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', ]


# Serializer object for courses app

from courses.models import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['course', 'number', 'title']