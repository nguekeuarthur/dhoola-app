# dhoola-app
Documentation du Projet Dhoola
Dhoola est une application mobile qui permet aux Camerounais vivant à l’étranger
d’acheter/payer directement les services de prestataires pour leurs proches restés au pays.
Ce projet est une plateforme de visualisation des données de Dhoola, développée avec
Streamlit, Plotly, et Firebase. Il permet d'explorer et d'analyser les métriques
d'utilisation de l'application Dhoola, y compris l'engagement des utilisateurs, les
tendances géographiques et les interactions avec l'application.
1. Architecture du Projet
L'application est organisée en plusieurs modules analytiques :
 Dashboard : Vue générale des statistiques clés.
 Usage : Analyse des utilisateurs (origine, appareils, pages visitées).
 Engagement : Étude de l'interaction et de l'engagement des utilisateurs.
 Maps : Analyse géographique des utilisateurs.
2. Technologies Utilisées
 Langage : Python
 Frameworks : Streamlit, Plotly
 Base de données : Firebase Firestore
 Bibliothèques : Pandas, Pandas-Datareader, Prophet, FPDF
3. Installation et Configuration
Prérequis
 Python 3.7+
 Un compte Firebase avec une clé de service JSON
Étapes d'installation
1. Cloner le projet :
2. git clone repository_url
3. cd dhoola-app
4. Installer les dépendances :
5. pip install -r requirements.txt
6. Ajouter la clé Firebase (myDhoola.json) au dossier du projet.
7. Lancer l'application :
8. streamlit run app.py4. Fonctionnalités
Dashboard
 Nombre total d'utilisateurs
 Nombre de sessions
 Taux de rétention
 Répartition par pays
Usage
 Analyse des utilisateurs (pays, appareils, sessions)
 Pages les plus visitées
Engagement
 Durée moyenne des sessions
 Nombre d’utilisateurs actifs (DAU, WAU, MAU)
 Taux de conversion
Maps
 Répartition géographique des utilisateurs
 Cartographie interactive
5. Explication des Fichiers
Fichier Description
app.py Point d’entrée principal, gère la navigation
Dashboard.py Affichage des statistiques générales
Usage.py Analyse des données utilisateur
Engagement.py Suivi de l’engagement
Maps.py Données géographiques
connect.py Connexion à Firebase
collectionAnalyseAndAll.py Récupération des données Firestore
requirements.txt Dépendances requises6. Utilisation
1. Lancer l'application : streamlit run app.py
2. Explorer les données via l’interface interactive.
3. Appliquer des filtres pour explorer des segments spécifiques.
4. Exporter des rapports PDF avec les statistiques clés.
7. Déploiement
L’application peut être déployée sur Streamlit Cloud ou Heroku.
Déploiement sur Streamlit Cloud
1. Ajouter le projet sur GitHub.
2. Lier le dépôt à Streamlit Cloud.
3. Ajouter les variables Firebase en tant que secrets.
4. Déployer 🚀.
8. Améliorations Possibles
✅ Optimisation des requêtes Firebase
✅ Gestion des permissions utilisateur
✅ Alertes automatisées en cas d’anomalie
🔹 Lien du projet déployé : Dhoola App
🔹 Auteur : Nguekeu Fonkeng Arthur (Data Analyst)
