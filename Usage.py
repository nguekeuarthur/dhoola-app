import streamlit as st
import pandas as pd
import plotly.express as px
import ast
from collections import Counter

# Charger les données
app_opened_time = pd.read_csv('appOpenedTime.csv')
sessions_with_pages_true = pd.read_csv('sessions_with_pages_true.csv')
users = pd.read_csv('users.csv')
prestataires = pd.read_csv('prestataires.csv')
transactions = pd.read_csv('transaction.csv')

# Convertir les colonnes de date en datetime
sessions_with_pages_true['session_start'] = pd.to_datetime(sessions_with_pages_true['session_start'])
sessions_with_pages_true['session_end'] = pd.to_datetime(sessions_with_pages_true['session_end'])
transactions['creationTime'] = pd.to_datetime(transactions['creationTime'])
users['creationTime'] = pd.to_datetime(users['creationTime'])

# Widgets interactifs pour le filtrage
selected_country = st.sidebar.multiselect("Sélectionnez les pays", options=users['country'].unique(), key='country_selector')
selected_device_type = st.sidebar.multiselect("Sélectionnez le type d'appareil", options=['Android', 'IOS'], key='device_type_selector')
date_range = st.sidebar.date_input("Sélectionnez la plage de dates", [])

# Filtrage des données selon les sélections
filtered_users = users.copy()
filtered_sessions = sessions_with_pages_true.copy()
filtered_transactions = transactions.copy()

# Filtrer les utilisateurs par pays
if selected_country:
    filtered_users = filtered_users[filtered_users['country'].isin(selected_country)]

# Filtrer les utilisateurs par type d'appareil
if selected_device_type:
    device_mapping = {'Android': True, 'IOS': False}
    filtered_users = filtered_users[filtered_users['isAndroid'].apply(lambda x: 'Android' if x else 'IOS').isin(selected_device_type)]

# Filtrer les données par la plage de dates sélectionnée
if len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
    filtered_users = filtered_users[(filtered_users['creationTime'] >= pd.Timestamp(start_date)) & 
                                    (filtered_users['creationTime'] <= pd.Timestamp(end_date))]
    filtered_sessions = filtered_sessions[(filtered_sessions['session_start'] >= pd.Timestamp(start_date)) & 
                                          (filtered_sessions['session_end'] <= pd.Timestamp(end_date))]
    filtered_transactions = filtered_transactions[(filtered_transactions['creationTime'] >= pd.Timestamp(start_date)) & 
                                                  (filtered_transactions['creationTime'] <= pd.Timestamp(end_date))]

# Normalisation et standardisation des noms de ville
if 'town' in filtered_users.columns:
    filtered_users['town'] = filtered_users['town'].fillna('').astype(str)
    filtered_users['town'] = filtered_users['town'].str.strip().str.lower()
    filtered_users['town'] = filtered_users['town'].replace({
        'yaounde': 'yaoundé',
        'douala, yaoundé et edea': 'yaoundé',
        'mélong, moungo-littoral': 'mélong',
    })
    filtered_users['town'] = filtered_users['town'].str.title()

# Appliquer les filtres aux sessions et transactions en fonction des utilisateurs filtrés
filtered_sessions = filtered_sessions[filtered_sessions['uid'].isin(filtered_users['uid'])]
filtered_transactions = filtered_transactions[filtered_transactions['prestataireUid'].isin(prestataires['uid'])]

# Analyser les données
user_country_distribution = filtered_users['country'].value_counts()
user_device_distribution = filtered_users['isAndroid'].apply(lambda x: 'Android' if x else 'IOS').value_counts()
average_session_duration = filtered_sessions['session_duration_in_seconds'].mean()
average_session_duration_minutes = average_session_duration / 60

# Analyser les pages visitées avec le filtrage
visited_pages_filtered = filtered_sessions['visited_pages'].apply(lambda x: ast.literal_eval(x))
all_visited_pages_filtered = [page for sublist in visited_pages_filtered for page in sublist]
page_counts_filtered = Counter(all_visited_pages_filtered)
most_common_pages_filtered = page_counts_filtered.most_common()
pages_df_filtered = pd.DataFrame(most_common_pages_filtered, columns=['Page', 'Visites'])

# Utilisateurs les plus actifs avec le filtrage
most_active_users_filtered = filtered_sessions['uid'].value_counts().reset_index()
most_active_users_filtered.columns = ['uid', 'session_count']
most_active_users_names_filtered = most_active_users_filtered.merge(filtered_users[['uid', 'first_name', 'last_name']], on='uid')

# Combiner les prénoms et noms de famille
most_active_users_names_filtered['full_name'] = most_active_users_names_filtered['first_name'] + ' ' + most_active_users_names_filtered['last_name']
most_active_users_names_filtered = most_active_users_names_filtered[['full_name', 'session_count']]

# Calcul des prestataires les plus actifs avec les filtres appliqués
most_active_prestataires_filtered = filtered_transactions['prestataireUid'].value_counts().reset_index()
most_active_prestataires_filtered.columns = ['prestataireUid', 'transaction_count']
most_active_prestataires_names_filtered = most_active_prestataires_filtered.merge(prestataires[['uid', 'companyName']], left_on='prestataireUid', right_on='uid')

# Utilisation du nom de l'entreprise pour les prestataires filtrés
most_active_prestataires_names_filtered = most_active_prestataires_names_filtered[['companyName', 'transaction_count']]

# Données démographiques (si disponibles)
if 'age' in users.columns:
    age_distribution = filtered_users['age'].value_counts()
else:
    age_distribution = None

if 'gender' in users.columns:
    gender_distribution = filtered_users['gender'].value_counts()
else:
    gender_distribution = None

# Canaux d'acquisition (si disponibles)
if 'source' in users.columns:
    acquisition_source = filtered_users['source'].value_counts()
else:
    acquisition_source = None

# Données géographiques détaillées (villes)
if 'town' in filtered_users.columns:
    city_distribution = filtered_users['town'].value_counts()

# Interface utilisateur Streamlit
st.title('Analyse des Données de l\'Application Dhoola')

# Distribution des utilisateurs par pays (Pie chart)
st.header('Distribution des Utilisateurs par Pays')
fig1 = px.pie(user_country_distribution, values=user_country_distribution, names=user_country_distribution.index, title='Répartition des Utilisateurs par Pays', hole=0.4)
fig1.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig1)

# Distribution des utilisateurs par type d'appareil (Donut chart)
st.header('Distribution des Utilisateurs par Type d\'Appareil')
fig2 = px.pie(user_device_distribution, values=user_device_distribution.values, names=user_device_distribution.index, title='Type d\'Appareil', hole=0.3)
fig2.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig2)

# Durée moyenne des sessions (Text output)
st.header('Durée Moyenne des Sessions')
st.metric(label="Durée Moyenne des Sessions", value=f"{average_session_duration_minutes:.2f} minutes")

# Données démographiques (Age distribution)
if age_distribution is not None:
    st.header('Répartition par Tranche d\'Âge')
    fig_age = px.histogram(age_distribution, x=age_distribution.index, y=age_distribution.values, title='Répartition par Tranche d\'Âge')
    st.plotly_chart(fig_age)

# Données démographiques (Gender distribution)
# if gender_distribution is not None:
#     st.header('Répartition par Genre')
#     fig_gender = px.pie(gender_distribution, values=gender_distribution.values, names=gender_distribution.index, title='Répartition par Genre', hole=0.4)
#     st.plotly_chart(fig_gender)

# Données géographiques détaillées (Cities)
if city_distribution is not None:
    st.header('Répartition des Utilisateurs par Ville')
    fig_city = px.bar(city_distribution, x=city_distribution.index, y=city_distribution.values, title='Répartition des Utilisateurs par Ville')
    st.plotly_chart(fig_city)

# Canaux d'acquisition (Source)
if acquisition_source is not None:
    st.header('Sources d\'Acquisition')
    fig_source = px.pie(acquisition_source, values=acquisition_source.values, names=acquisition_source.index, title='Sources d\'Acquisition', hole=0.3)
    st.plotly_chart(fig_source)

# Pages les plus visitées (Horizontal bar chart) avec filtrage
st.header('Pages les Plus Visitées (Services les Plus Utilisés)')
fig4 = px.bar(pages_df_filtered, x='Visites', y='Page', orientation='h', title='Pages les Plus Visitées')
st.plotly_chart(fig4)

# Utilisateurs les plus actifs (Bubble chart)
st.header('Utilisateurs les Plus Actifs')
fig5 = px.scatter(most_active_users_names_filtered, x='full_name', y='session_count', size='session_count', title='Utilisateurs les Plus Actifs')
fig5.update_layout(xaxis_title='Utilisateur', yaxis_title='Nombre de Sessions')
st.plotly_chart(fig5)

# Prestataires les plus actifs (Bar chart)
st.header('Prestataires les Plus Actifs')
fig6 = px.bar(most_active_prestataires_names_filtered, 
              x='transaction_count', 
              y='companyName', 
              orientation='h', 
              title='Prestataires les Plus Actifs',
              labels={'transaction_count':'Nombre de Transactions', 'companyName':'Entreprise'})

# Mettre à jour la disposition pour améliorer la lisibilité
fig6.update_layout(xaxis_title='Nombre de Transactions', yaxis_title='Entreprise')
st.plotly_chart(fig6)
