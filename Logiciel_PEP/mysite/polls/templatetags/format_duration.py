from django import template
from django.utils import timesince
from django.db.models import Sum, F
from polls.models import AssignationJEH
register = template.Library()

@register.filter(name='format_duration')
def format_duration(value):
    if value.total_seconds() < 3600:
        # Less than an hour
        minutes = int(value.total_seconds() // 60)
        return f"{minutes} min"
    elif value.total_seconds() < 86400:
        # Less than a day
        hours = int(value.total_seconds() // 3600)
        return f"{hours} h"
    else:
        # Number of days
        days = int(value.total_seconds() // 86400)
        return f"{days} days"
    
@register.filter(name='assignation')
def assignation(eleve, etude):
    return list(AssignationJEH.objects.filter(eleve=eleve, phase__etude=etude))

@register.filter(name='JEH')
def JEH(eleve, etude):
    queryset = AssignationJEH.objects.filter(eleve=eleve, phase__etude=etude)
    nb_total_JEH = queryset.aggregate(total_sum=Sum('nombre_JEH'))['total_sum'] or 0

    # Calculate the total monetary amount manually using the model's method
    montant_total = sum(assignment.retribution_brute_totale() for assignment in queryset)

    return f"{nb_total_JEH} JEH pour un montant de {montant_total:.2f}€ HT"

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)