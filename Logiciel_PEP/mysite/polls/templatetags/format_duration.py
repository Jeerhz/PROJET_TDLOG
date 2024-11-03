from django import template
from django.utils import timesince
from django.db.models import Sum, F
from polls.models import AssignationJEH
from num2words import num2words
from datetime import datetime, timedelta
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
    JEH= "JEH"
    if nb_total_JEH>1:
        JEH= "JEHs"

    # Calculate the total monetary amount manually using the model's method
    montant_total = sum(assignment.retribution_brute_totale() for assignment in queryset)

    return f"{nb_total_JEH} {JEH} pour un montant de {montant_total:.2f}€ HT"

@register.filter(name="cumulPhase")
def cumulPhase(eleve, phase):
    return phase.get_nb_JEH_eleve(eleve)

@register.filter("phasesEtude")
def phasesEtude(eleve, etude):
    return eleve.phases_etude(etude)

@register.filter("nbPhasesEtude")
def nbPhasesEtude(eleve, etude):
    return eleve.phases_etude(etude).count()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='montantFacturePhase')
def montant_fac_phase(facture, phase):
    return phase.montant_HT_par_JEH*facture.pourcentage_JEH*phase.nb_JEH/100

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
@register.filter(name='Range_boucle')
def range_boucle(start, end):
    return range(start, end+1)

@register.filter(name='ChiffreLettre')
def chiffre_lettres(nombre):
    if nombre is None:
        return ''
    nbr_arrondi = round(float(nombre),2)
    nbr_entier = int(nbr_arrondi)
    nbr_dec = int(round((nbr_arrondi - nbr_entier)*100)) 
    lettres_entier = num2words(nbr_entier, lang='fr')  
    lettres_deci = num2words(nbr_dec, lang='fr')
    centimes = 'centimes'
    if nbr_dec <2:
        centimes = 'centime'
    return f"{lettres_entier} euros et {lettres_deci} {centimes}"

@register.filter(name='EnLettres')
def en_lettres(nombre):
    if nombre is None:
        return ''
    else:
        return num2words(nombre, lang='fr')  
     
     

@register.filter(name='FormatNombres')
def format_nombres(nombre):
    arrondi = round(nombre, 2)
    nbre_virg = f"{arrondi:.2f}".replace('.', ',')
    return nbre_virg

@register.filter(name='RefMission')
def ref_mission(numero):
    date = datetime.now()
    annee = str(date.year)
    an =annee[-2:]
    return f"{an}e{numero:02d}"

@register.filter(name='RefFacture') 
def ref_facture(numero):
    date = datetime.now()
    annee = str(date.year)
    an =annee[-2:]
    return f"{an}{numero:03d}"

@register.filter(name='SupA')
def superieur_a(value, arg):
    try:
        return int(value) > int(arg)
    except (ValueError, TypeError):
        return False

@register.filter(name='dateJJMM')
def datejjmm(date):
    return date.strftime("%d/%m")
    

@register.filter
def order_dict_by_keys(dictionary):
    """
    Custom template filter to order a dictionary by a predefined list of keys.
    Only includes keys that exist in the dictionary.
    :param dictionary: The dictionary to be ordered (e.g., etude.suivi_document)
    :return: A list of tuples (key, value) in the specified order
    """

    # Define the hardcoded order of keys
    ordered_keys = [
        'Devis', 'CE', 'Validation des Intervenants', 'RDM', 
        "Facture d'Acompte", 'PVRF', "Facture de Solde", 
        "QS Etudiant", "QS Client", "BV (Etudiants payés)", 
        "Echange Client", "Livrables"
    ]

    # Filter `ordered_keys` to include only keys that exist in the dictionary
    filtered_ordered_keys = [key for key in ordered_keys if key in dictionary]
    
    # Find any remaining keys that are in the dictionary but not in the filtered order
    missing_keys = set(dictionary.keys()) - set(filtered_ordered_keys)
    
    # Combine filtered ordered keys with the remaining keys
    full_ordered_keys = filtered_ordered_keys + sorted(missing_keys)

    # Create a list of tuples ordered by the full ordered keys
    ordered_dict = [(key, dictionary[key]) for key in full_ordered_keys if key in dictionary]
    
    return ordered_dict


