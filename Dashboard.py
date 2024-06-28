import streamlit as st
import pandas as pd
import plotly.express as px
from babel.dates import format_datetime

# Chargement des données CSV
users_df = pd.read_csv('users.csv')
app_opened_time_df = pd.read_csv('appOpenedTime.csv')
sessions_df = pd.read_csv('sessions_with_pages_true.csv')

# Conversion des colonnes de temps en datetime
app_opened_time_df['time'] = pd.to_datetime(app_opened_time_df['time'])
sessions_df['session_start'] = pd.to_datetime(sessions_df['session_start'])
sessions_df['session_end'] = pd.to_datetime(sessions_df['session_end'])
users_df['creationTime'] = pd.to_datetime(users_df['creationTime'])

# Ajout d'un sélecteur de date pour filtrer les données
st.sidebar.header("Filtre de date")
start_date = st.sidebar.date_input("Date de début", value=pd.to_datetime('2023-01-01'))
end_date = st.sidebar.date_input("Date de fin", value=pd.to_datetime('today'))

# Filtrage des données en fonction de la plage de dates sélectionnée
filtered_users_df = users_df[(users_df['creationTime'] >= pd.to_datetime(start_date)) & (users_df['creationTime'] <= pd.to_datetime(end_date))]
filtered_app_opened_time_df = app_opened_time_df[(app_opened_time_df['time'] >= pd.to_datetime(start_date)) & (app_opened_time_df['time'] <= pd.to_datetime(end_date))]
filtered_sessions_df = sessions_df[(sessions_df['session_start'] >= pd.to_datetime(start_date)) & (sessions_df['session_end'] <= pd.to_datetime(end_date))]

# Calcul des statistiques nécessaires sur les données filtrées
total_users = len(filtered_users_df)
active_users = len(filtered_users_df[filtered_users_df['status'] == 'active'])

# Calculer les jours actifs en comptant les jours uniques où l'application a été ouverte
days_active = len(filtered_app_opened_time_df['time'].dt.date.unique())

new_users = len(filtered_users_df[pd.to_datetime(filtered_users_df['creationTime']).dt.date == pd.to_datetime('today').date()])
countries = filtered_users_df['country'].nunique()
users_by_gender = filtered_users_df['gender'].value_counts().reset_index()
users_by_gender.columns = ['gender', 'count']

# Préparation des données pour la carte et le graphique à barres
country_counts = filtered_users_df['country'].value_counts().reset_index()
country_counts.columns = ['country', 'count']

# Création de la carte avec Plotly
fig_map = px.choropleth(country_counts,
                        locations="country",
                        locationmode="country names",
                        color="count",
                        hover_name="country",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Utilisateurs par pays")

# Utilisation de Babel pour obtenir le nom des jours en français
def get_day_name(date, locale='fr_FR'):
    return format_datetime(date, 'EEEE', locale=locale)

# Appliquer la fonction pour obtenir les noms de jours
filtered_app_opened_time_df['day_of_week'] = filtered_app_opened_time_df['time'].apply(get_day_name)

# Préparation des données pour le graphique à barres des utilisateurs actifs par jour de la semaine
active_users_by_day = filtered_app_opened_time_df['day_of_week'].value_counts().reindex([
    'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'
]).reset_index()
active_users_by_day.columns = ['day', 'count']

# Création du graphique à barres avec Plotly pour les utilisateurs actifs par jour de la semaine
fig_active_users_bar = px.bar(active_users_by_day,
                              x='day',
                              y='count',
                              title='Nombre d\'utilisateurs actifs par jour de la semaine',
                              labels={'day': 'Jour de la semaine', 'count': 'Nombre d\'utilisateurs actifs'},
                              color='count',
                              color_continuous_scale=px.colors.sequential.Blues)

# Création du graphique à barres avec Plotly pour les utilisateurs par pays
fig_bar = px.bar(country_counts,
                 x='country',
                 y='count',
                 title='Nombre d\'utilisateurs par pays',
                 labels={'country': 'Pays', 'count': 'Nombre d\'utilisateurs'})

# Création du graphique en camembert pour les utilisateurs par genre
fig_pie = px.pie(users_by_gender,
                 names='gender',
                 values='count',
                 title='Répartition des utilisateurs par genre')

# Affichage du tableau de bord
st.title("Tableau de bord de l'Application")

total1, total2, total3, total4, total5 = st.columns(5, gap='large')

with total1:
    st.success("Total User")
    st.metric(label="Total Users", value=f"{total_users:,.0f}")

with total2:
    st.info("Nombre Utilisateur Actif")
    st.metric(label="Active Users", value=f"{active_users:,.0f}")

with total3:
    st.info("Jours Actifs")
    st.metric(label="Active Days", value=f"{days_active:,.0f}")

with total4:
    st.info("Inscription User")
    st.metric(label="New Users Today", value=f"{new_users:,.0f}")

with total5:
    st.info("Countries")
    st.metric(label="Countries", value=countries)

# Additional Charts
st.plotly_chart(fig_map, use_container_width=True)
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_active_users_bar, use_container_width=True)

st.header("Utilisateur par genre")
st.plotly_chart(fig_pie, use_container_width=True)
