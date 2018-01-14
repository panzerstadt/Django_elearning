from django.db import models

# this file will hold the models that are related to students
# keeps student files separate from main server
# custom user model here, for a 'student' model

from django.contrib.auth.models import AbstractUser
from django.db import models

# subclass our user class
# setting a custom user model (that is basically a copy of the default model allows
# us to migrate user models much easier later in the project

# in the database, you can see that the naming follows the convention 'appName_modelName'
# app is called 'elearning'
# the first model(read: database) is called 'courses'. the other one is called 'students'
# in here, the 'students' model uses a class User to represent the model
class User(AbstractUser):
    pass
