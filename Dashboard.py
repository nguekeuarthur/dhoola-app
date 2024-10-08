import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast

# Charger les données
users = pd.read_csv('users.csv')
sessions = pd.read_csv('sessions_with_pages_true.csv')

# Convertir les colonnes de date en datetime si nécessaire
if 'creationTime' in users.columns:
    users['creationTime'] = pd.to_datetime(users['creationTime'], errors='coerce')

if 'session_start' in sessions.columns:
    sessions['session_start'] = pd.to_datetime(sessions['session_start'], errors='coerce')
if 'session_end' in sessions.columns:
    sessions['session_end'] = pd.to_datetime(sessions['session_end'], errors='coerce')

# Calcul des statistiques générales
nombre_de_sessions = len(sessions)
nombre_total_utilisateurs = len(users)
taux_retention = (nombre_de_sessions / nombre_total_utilisateurs) * 100 if nombre_total_utilisateurs > 0 else 0
nombre_pages_par_session = sessions['visited_pages'].apply(lambda x: len(ast.literal_eval(x))).mean()
temps_ecoule_moyen = sessions['session_duration_in_seconds'].sum() / 60  # Convertir en minutes
nombre_de_pays = users['country'].nunique()

# Affichage des statistiques générales avec couleurs personnalisées
st.title('Tableau de Bord Centralisé - Application Dhoola')

st.subheader('Statistiques Générales')
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div style='background-color: #e0f7fa; padding: 10px; border-radius: 5px;'><strong>Nombre de Sessions</strong><br><h3>{}</h3></div>".format(nombre_de_sessions), unsafe_allow_html=True)
with col2:
    st.markdown("<div style='background-color: #fff3e0; padding: 10px; border-radius: 5px;'><strong>Nombre Total d'Utilisateurs</strong><br><h3>{}</h3></div>".format(nombre_total_utilisateurs), unsafe_allow_html=True)
with col3:
    st.markdown("<div style='background-color: #e3f2fd; padding: 10px; border-radius: 5px;'><strong>Taux de Rétention (%)</strong><br><h3>{:.2f}</h3></div>".format(taux_retention), unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown("<div style='background-color: #f3e5f5; padding: 10px; border-radius: 5px;'><strong>Nombre de Pages par Session</strong><br><h3>{:.2f}</h3></div>".format(nombre_pages_par_session), unsafe_allow_html=True)
with col5:
    st.markdown("<div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px;'><strong>Nombre de Pays</strong><br><h3>{}</h3></div>".format(nombre_de_pays), unsafe_allow_html=True)
with col6:
    st.markdown("<div style='background-color: #ffebee; padding: 10px; border-radius: 5px;'><strong>Temps Écoulé Moyen (minutes)</strong><br><h3>{:.2f}</h3></div>".format(temps_ecoule_moyen), unsafe_allow_html=True)

# 1. Répartition Géographique Globale (de Maps.py)
st.subheader('Répartition Géographique Globale')
if 'country' in users.columns:
    user_country_density = users['country'].value_counts().reset_index()
    user_country_density.columns = ['country', 'count']
    
    fig_continent = px.choropleth(user_country_density, locations='country', locationmode='country names',
                                  color='count', hover_name='country', hover_data=['count'], 
                                  title='Utilisateurs par Pays et Continent', projection='natural earth')
    fig_continent.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="LightGray",
                              showocean=True, oceancolor="LightBlue")
    st.plotly_chart(fig_continent, use_container_width=True)
else:
    st.warning("La colonne 'country' n'est pas présente dans le DataFrame `users`.")

# 2. Pages les Plus Visitées (de Engagement.py)
st.subheader('Pages les Plus Visitées')
visited_pages = sessions['visited_pages'].apply(lambda x: ast.literal_eval(x))
all_visited_pages = [page for sublist in visited_pages for page in sublist]
page_counts = pd.Series(all_visited_pages).value_counts().reset_index()
page_counts.columns = ['Page', 'Visites']

fig_pages = px.bar(page_counts, x='Visites', y='Page', orientation='h', title='Pages les Plus Visitées')
st.plotly_chart(fig_pages, use_container_width=True)

# 3. Nombre d'Utilisateurs Actifs par Jour de la Semaine (de Maps.py)
st.subheader('Nombre d\'Utilisateurs Actifs par Jour de la Semaine')
if 'session_start' in sessions.columns:
    sessions['day_of_week'] = sessions['session_start'].dt.day_name()
    active_users_per_day = sessions.groupby('day_of_week').size().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')
    
    fig_users_per_day = px.bar(active_users_per_day, x='day_of_week', y='count',
                               title='Nombre d\'Utilisateurs Actifs par Jour de la Semaine',
                               labels={'day_of_week': 'Jour de la Semaine', 'count': 'Nombre d\'Utilisateurs'},
                               color='day_of_week')
    st.plotly_chart(fig_users_per_day, use_container_width=True)
else:
    st.warning("La colonne 'session_start' n'est pas présente dans le DataFrame `sessions`.")

# 4. Durée Moyenne des Sessions (de Engagement.py)
# st.subheader('Durée Moyenne des Sessions')
# if 'session_duration_in_seconds' in sessions.columns:
#     sessions['session_duration_in_minutes'] = sessions['session_duration_in_seconds'] / 60
#     average_session_duration = sessions['session_duration_in_minutes'].mean()

#     st.metric(label="Durée Moyenne des Sessions", value=f"{average_session_duration:.2f} minutes")
# else:
#     st.warning("La colonne 'session_duration_in_seconds' n'est pas présente dans le DataFrame `sessions`.")

# 5. Répartition par Type d'Appareil (de Usage.py)
st.subheader('Répartition par Type d\'Appareil')
if 'isAndroid' in users.columns:
    device_distribution = users['isAndroid'].apply(lambda x: 'Android' if x else 'iOS').value_counts().reset_index()
    device_distribution.columns = ['Appareil', 'Nombre d\'Utilisateurs']

    fig_device = px.pie(device_distribution, values='Nombre d\'Utilisateurs', names='Appareil', 
                        title='Répartition par Type d\'Appareil', hole=0.3)
    st.plotly_chart(fig_device, use_container_width=True)
else:
    st.warning("La colonne 'isAndroid' n'est pas présente dans le DataFrame `users`.")
