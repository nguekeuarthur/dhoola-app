import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Widgets interactifs pour le filtrage
selected_country = st.sidebar.multiselect("Sélectionnez les pays", options=users['country'].unique(), key='country_selector')
date_range = st.sidebar.date_input("Sélectionnez la plage de dates", [])

# Filtrage des données selon les sélections
filtered_users = users.copy()
filtered_sessions = sessions.copy()

# Filtrer par pays
if selected_country:
    filtered_users = filtered_users[filtered_users['country'].isin(selected_country)]

# Filtrer par la plage de dates sélectionnée
if len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
    filtered_users = filtered_users[(filtered_users['creationTime'] >= pd.Timestamp(start_date)) & 
                                    (filtered_users['creationTime'] <= pd.Timestamp(end_date))]
    filtered_sessions = filtered_sessions[(filtered_sessions['session_start'] >= pd.Timestamp(start_date)) & 
                                          (filtered_sessions['session_end'] <= pd.Timestamp(end_date))]

# Carte mondiale avec segmentation par continent
st.subheader('Répartition Géographique Globale')
if 'country' in filtered_users.columns:
    fig_continent = px.choropleth(filtered_users, locations='country', locationmode='country names',
                                  color='country', hover_name='country', title='Utilisateurs par Pays et Continent',
                                  projection='natural earth')
    fig_continent.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="LightGray",
                              showocean=True, oceancolor="LightBlue")
    st.plotly_chart(fig_continent, use_container_width=True)
else:
    st.warning("La colonne 'country' n'est pas présente dans le DataFrame filtered_users.")



# 2. Activité des Utilisateurs par Ville
# st.subheader('Activité des Utilisateurs par Ville')
# if 'town' in filtered_users.columns:
#     user_city_activity = filtered_users['town'].value_counts().reset_index()
#     user_city_activity.columns = ['town', 'count']
    
#     fig_city_activity = px.bar(user_city_activity, x='count', y='town', orientation='h',
#                                title='Activité des Utilisateurs par Ville',
#                                labels={'count': 'Nombre d\'Utilisateurs', 'town': 'Ville'})
#     st.plotly_chart(fig_city_activity, use_container_width=True)
# else:
#     st.warning("La colonne 'town' n'est pas présente dans le DataFrame `filtered_users`.")

# 3. Carte de Chaleur (Heatmap) de l'Activité des Utilisateurs
# st.subheader('Carte de Chaleur de l\'Activité des Utilisateurs')
# if 'latitude' in filtered_users.columns and 'longitude' in filtered_users.columns:
#     fig_heatmap = go.Figure(go.Densitymapbox(lat=filtered_users['latitude'], lon=filtered_users['longitude'],
#                                              z=filtered_users.index, radius=10,
#                                              colorscale='Viridis', zmin=0, zmax=10,
#                                              showscale=True))
#     fig_heatmap.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=0,
#                               mapbox_center_lat=0, mapbox_zoom=1)
#     fig_heatmap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     st.plotly_chart(fig_heatmap, use_container_width=True)
# else:
#     st.warning("Les colonnes 'latitude' et 'longitude' ne sont pas présentes dans le DataFrame `filtered_users`.")

# 4. Segmentation par Type d'Appareil et Localisation
st.subheader('Segmentation par Type d\'Appareil et Localisation')
if 'country' in filtered_users.columns and 'isAndroid' in filtered_users.columns:
    user_device_country = filtered_users.groupby(['country', 'isAndroid']).size().reset_index(name='count')
    user_device_country['device'] = user_device_country['isAndroid'].apply(lambda x: 'Android' if x else 'iOS')
    
    fig_device_country = px.bar(user_device_country, x='count', y='country', color='device',
                                title='Segmentation par Type d\'Appareil et Localisation',
                                labels={'count': 'Nombre d\'Utilisateurs', 'country': 'Pays'})
    st.plotly_chart(fig_device_country, use_container_width=True)
else:
    st.warning("Les colonnes 'country' et 'isAndroid' ne sont pas présentes dans le DataFrame `filtered_users`.")

# 5. Analyse des Sessions par Localisation
# st.subheader('Analyse des Sessions par Localisation')
# if 'country' in filtered_sessions.columns:
#     country_sessions = filtered_sessions['country'].value_counts().reset_index()
#     country_sessions.columns = ['country', 'sessions']
    
#     fig_sessions_country = px.choropleth(country_sessions, locations='country', locationmode='country names',
#                                          color='sessions', hover_name='country',
#                                          title='Analyse des Sessions par Localisation',
#                                          projection='mercator', color_continuous_scale='Oranges')
#     fig_sessions_country.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="LightGray",
#                                      showocean=True, oceancolor="LightBlue")
#     fig_sessions_country.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#     st.plotly_chart(fig_sessions_country, use_container_width=True)
# else:
#     st.warning("La colonne 'country' n'est pas présente dans le DataFrame `filtered_sessions`.")

# 6. Carte Interactive avec Zoom Multi-Niveaux
# st.subheader('Carte Interactive avec Zoom Multi-Niveaux')
# if 'country' in filtered_users.columns:
#     fig_multilevel_zoom = px.scatter_geo(filtered_users, locations='country', locationmode='country names',
#                                          hover_name='country', color='country', 
#                                          title='Carte Interactive avec Zoom Multi-Niveaux')
#     fig_multilevel_zoom.update_geos(showcoastlines=True, coastlinecolor="Black", showland=True, landcolor="LightGray",
#                                     showocean=True, oceancolor="LightBlue")
#     fig_multilevel_zoom.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, dragmode='zoom')
#     st.plotly_chart(fig_multilevel_zoom, use_container_width=True)
# else:
#     st.warning("La colonne 'country' n'est pas présente dans le DataFrame `filtered_users`.")

# 7. Tendances Géographiques au Fil du Temps
st.subheader('Tendances Géographiques au Fil du Temps')
if 'creationTime' in filtered_users.columns and 'country' in filtered_users.columns:
    filtered_users['year_month'] = filtered_users['creationTime'].dt.to_period('M').astype(str)
    geo_trend = filtered_users.groupby(['year_month', 'country']).size().reset_index(name='count')
    
    fig_geo_trend = px.line(geo_trend, x='year_month', y='count', color='country',
                             title='Tendances Géographiques au Fil du Temps',
                             labels={'year_month': 'Période', 'count': 'Nombre d\'Utilisateurs'},
                             markers=True)
    
    st.plotly_chart(fig_geo_trend, use_container_width=True)
else:
    st.warning("Les colonnes 'creationTime' et 'country' ne sont pas présentes dans le DataFrame `filtered_users`.")
# 8. Nombre d'Utilisateurs Actifs par Jour de la Semaine
st.subheader('Nombre d\'Utilisateurs Actifs par Jour de la Semaine')
if 'session_start' in filtered_sessions.columns:
    filtered_sessions['day_of_week'] = filtered_sessions['session_start'].dt.day_name()
    active_users_per_day = filtered_sessions.groupby('day_of_week').size().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')
    
    fig_users_per_day = px.bar(active_users_per_day, x='day_of_week', y='count',
                               title='Nombre d\'Utilisateurs Actifs par Jour de la Semaine',
                               labels={'day_of_week': 'Jour de la Semaine', 'count': 'Nombre d\'Utilisateurs'},
                               color='day_of_week')
    st.plotly_chart(fig_users_per_day, use_container_width=True)
else:
    st.warning("La colonne 'session_start' n'est pas présente dans le DataFrame `filtered_sessions`.")
