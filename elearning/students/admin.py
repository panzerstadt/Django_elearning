from django.contrib import admin

# this import allows us to build a user class with more security features
# if users were made before this was done, then we gotta change the password again, using
# 'manage.py changepassword username' and key it in in CLI
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from students.models import User

# makes an admin for the app by inheriting from django's default model admin
class UserAdmin(BaseUserAdmin):
    pass

# then register the database to lock it from random changes, using CourseAdmin as the administrator of this model (db)
admin.site.register(User, UserAdmin)
