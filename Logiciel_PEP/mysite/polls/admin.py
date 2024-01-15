from django.contrib import admin

from .models import JE, User, Client, Etude, Student

admin.site.register(JE)

admin.site.register(User)
admin.site.register(Client)
admin.site.register(Etude)
admin.site.register(Student)



