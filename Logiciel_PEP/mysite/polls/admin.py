from django.contrib import admin

from .models import JE, Client, Etude, Student, Member, Message, Phase, AssignationJEH, Candidature, Facture, Notification

admin.site.register(JE)

admin.site.register(Member)
admin.site.register(Client)
admin.site.register(Etude)
admin.site.register(Student)
admin.site.register(Message)
admin.site.register(Phase)
admin.site.register(AssignationJEH)
admin.site.register(Candidature)
admin.site.register(Facture)
admin.site.register(Notification)



