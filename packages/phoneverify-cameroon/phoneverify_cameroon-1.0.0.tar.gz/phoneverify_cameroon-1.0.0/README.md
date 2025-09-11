# PhoneVerify Mobile Money Cameroun

> **API de validation des numeros de telephone mobile money pour le Cameroun**  
> Validation, detection d'operateurs et conversion de formats pour MTN et Orange Mobile Money

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16+-orange.svg)](https://django-rest-framework.org)
[![API](https://img.shields.io/badge/API-REST-red.svg)](http://127.0.0.1:8000/api/v1/docs/)


## **Probleme**
Chaque jour, des milliers de transactions échouent pour des raisons évitables: Formats inconsistants, Confusion opérateur, Erreurs de saisie etc..

50+ startups fintech développent CHACUNE leur propre validateur

Inconsistance : Chaque solution a ses propres règles

Maintenance coûteuse : Mise à jour lors de changements réglementaires

Barrière à l'entrée : Les nouvelles startups perdent du temps sur ce problème basique.

Le Cameroun est le leader du mobile money en zone CEMAC avec 96% des transactions. Cependant, **0,5% des transactions echouent** , representant **2,5 milliards FCFA bloques** annuellement. 


**Solution :** API Open Source de validation des numeros mobile money camerounais(ORANGE & MTN).


## **Fonctionnalites**

### *Validation**
- Validation format camerounais 
- Detection automatique operateur
- 33 prefixes supportes
- Gestion multiple formats d'entree

### **APIs REST**
- **Validation simple** : `/api/v1/validate/`
- **Validation en masse** : `/api/v1/validate/batch/` (max 100)
- **Detection operateurs** : `/api/v1/detect/`
- **Conversion formats** : `/api/v1/convert/`

### **Documentation**
- **Swagger UI** : `/api/v1/docs/`
- **ReDoc** : `/api/v1/redoc/`
- **Health Check** : `/api/v1/health/`


### **Installation**

```bash
# Cloner le projet
git clone [URL_REPO]
cd "PhoneVerify Mobile Money CM"

# Environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependances
pip install -r requirements.txt

# Base de donnees
python manage.py migrate
python manage.py populate_prefixes

# Serveur
python manage.py runserver
```

*Developpe par Djoko Christian avec 💖 pour l'ecosysteme local*