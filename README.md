#  Application Web de Détection du Cancer de la Peau par Intelligence Artificielle

## Description

Cette application web permet de détecter automatiquement la présence potentielle d’un cancer de la peau à partir d’une image dermatologique grâce à un modèle d’intelligence artificielle basé sur le Deep Learning.

Le système utilise un modèle CNN pré-entraîné **VGG16** afin de classifier les lésions cutanées en deux catégories :

- ✅ Benign (bénigne)
- ⚠️ Malignant (maligne)

L’application offre également :

- une authentification utilisateur,
- l’enregistrement des patients,
- le stockage des résultats d’analyse,
- l’affichage de l’historique des patients.

---

# Technologies Utilisées

## Backend
- Python
- Flask

## Intelligence Artificielle
- TensorFlow / Keras
- VGG16
- NumPy

## Frontend
- HTML5
- CSS3
- Bootstrap

## Base de Données
- MySQL (XAMPP / phpMyAdmin)

---

# Structure du Projet

```bash
project/
│
├── app.py
├── requirements.txt
├── README.md
│
├── model/
│   └── vgg16_skin_cancer.keras
│
├── static/
│   └── uploads/
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── predict.html
│   ├── results.html
│   └── patients.html
│
└── database/
## 📸 Captures d'écran

### 🔐 Page de Login
![Login](https://raw.githubusercontent.com/aya-ben-chaieb/skin-cancer-flask-app/master/static/captures/login-user.png)

### 🏠 Page d'Accueil
![Home Page](https://raw.githubusercontent.com/aya-ben-chaieb/skin-cancer-flask-app/master/static/captures/home-page.png)

### 📊 Dashboard - Ajout Patient
![Dashboard](https://raw.githubusercontent.com/aya-ben-chaieb/skin-cancer-flask-app/master/static/captures/ajoutnouveau-patient.png)

### 🔬 Résultat Diagnostic
![Diagnostic](https://raw.githubusercontent.com/aya-ben-chaieb/skin-cancer-flask-app/master/static/captures/resultat-diagnostic.png)