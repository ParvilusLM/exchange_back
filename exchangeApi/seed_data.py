from exchangeApi.models import *
from decimal import Decimal
from django.utils.text import slugify


#### Creer les instances de taux de change, la monnaie locale est HTG ####

### Monnaie locale HTG ###
taux_de_change1 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='HTG',
    taux_du_jour=1.00
)

### Monnaie etrangere USD ### 
taux_de_change2 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='USD',
    taux_du_jour=131.65,
    est_reference=True
)

### Monnaie etrangere EUR ###
taux_de_change3 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='EUR',
    taux_du_jour=144.33
)

### Monnaie etrangere DOP ###
taux_de_change4 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='DOP',
    taux_du_jour=2.07
)

### Monnaie etrangere CLP ###
taux_de_change5 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='CLP',
    taux_du_jour=0.14
)

### Monnaie etrangere CAD ###
taux_de_change6 = TauxDeChange.objects.create(
    monnaie_locale='HTG',
    monnaie_etrangere='CAD',
    taux_du_jour=92.37
)


# instructtion pour executer le script
# python manage.py shell < exchangeApi/seed_data.py