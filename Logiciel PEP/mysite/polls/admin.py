from django.contrib import admin

from .models import JE, Client, Etude, Student, Member

admin.site.register(JE)

admin.site.register(Member)
admin.site.register(Client)
admin.site.register(Etude)
admin.site.register(Student)



