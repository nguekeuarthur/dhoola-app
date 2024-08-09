import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast
from collections import Counter
from fpdf import FPDF
import plotly.io as pio
import kaleido
import tempfile
import os

# Charger les données
app_opened_time = pd.read_csv('appOpenedTime.csv')
sessions_with_pages_true = pd.read_csv('sessions_with_pages_true.csv')
users = pd.read_csv('users.csv')
button_pressed_time = pd.read_csv('buttonPressedTime.csv')

# Convertir les colonnes de date en datetime
app_opened_time['time'] = pd.to_datetime(app_opened_time['time'])
sessions_with_pages_true['session_start'] = pd.to_datetime(sessions_with_pages_true['session_start'])
sessions_with_pages_true['session_end'] = pd.to_datetime(sessions_with_pages_true['session_end'])

# Widgets interactifs pour le filtrage
selected_country = st.sidebar.multiselect("Sélectionnez les pays", options=users['country'].unique(), key='country_selector')
selected_device_type = st.sidebar.multiselect("Sélectionnez le type d'appareil", options=['Android', 'IOS'], key='device_type_selector')
date_range = st.sidebar.date_input("Sélectionnez la plage de dates", [])

# Filtrage des données selon les sélections
filtered_users = users.copy()
if selected_country:
    filtered_users = filtered_users[filtered_users['country'].isin(selected_country)]
if selected_device_type:
    device_mapping = {'Android': True, 'IOS': False}
    filtered_users = filtered_users[filtered_users['isAndroid'].apply(lambda x: 'Android' if x else 'IOS').isin(selected_device_type)]

# Vérifier si une plage de dates complète est sélectionnée
if len(date_range) == 2:
    start_date, end_date = date_range[0], date_range[1]
    filtered_sessions = sessions_with_pages_true[
        (sessions_with_pages_true['session_start'] >= pd.Timestamp(start_date)) &
        (sessions_with_pages_true['session_end'] <= pd.Timestamp(end_date)) &
        (sessions_with_pages_true['uid'].isin(filtered_users['uid']))
    ]
else:
    # st.warning("Veuillez sélectionner une plage de deux dates.")
    filtered_sessions = sessions_with_pages_true[sessions_with_pages_true['uid'].isin(filtered_users['uid'])]


# Convertir les durées des sessions en minutes
filtered_sessions['session_duration_in_minutes'] = filtered_sessions['session_duration_in_seconds'] / 60

# Analyser les données avec les filtres appliqués
sessions_filtered = filtered_sessions.copy()
average_session_duration_minutes_filtered = sessions_filtered['session_duration_in_minutes'].mean()
sessions_per_user_filtered = sessions_filtered.groupby('uid').size()
average_sessions_per_user_filtered = sessions_per_user_filtered.mean()
users_daily_filtered = sessions_per_user_filtered[sessions_per_user_filtered == 1].count()
users_weekly_filtered = sessions_per_user_filtered[(sessions_per_user_filtered > 1) & (sessions_per_user_filtered <= 7)].count()
users_monthly_filtered = sessions_per_user_filtered[sessions_per_user_filtered > 7].count()
dau_filtered = sessions_filtered['session_start'].dt.date.value_counts().mean()
wau_filtered = sessions_filtered['session_start'].dt.to_period('W').value_counts().mean()
mau_filtered = sessions_filtered['session_start'].dt.to_period('M').value_counts().mean()
total_signups_filtered = len(filtered_users)
total_purchases_filtered = len(sessions_filtered)  # Remplacer par le nombre d'achats si disponible
conversion_rate_filtered = (total_purchases_filtered / total_signups_filtered) * 100 if total_signups_filtered > 0 else 0

# Graphiques avec filtres appliqués
fig_engagement_distribution_filtered = px.pie(pd.DataFrame({
    'Fréquence': ['Quotidienne', 'Hebdomadaire', 'Mensuelle'],
    'Utilisateurs': [users_daily_filtered, users_weekly_filtered, users_monthly_filtered]
}), names='Fréquence', values='Utilisateurs', title='Répartition des Utilisateurs par Fréquence d\'Utilisation (Filtrée)')

# Mise à jour du graphique : DAU, WAU, MAU comme des lignes séparées avec filtres
fig_active_users_filtered = go.Figure()

# DAU - Utilisateurs Actifs Quotidiens
valeurs_dau_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.date).size()
fig_active_users_filtered.add_trace(go.Scatter(x=valeurs_dau_filtered.index, y=valeurs_dau_filtered, mode='lines', name='DAU', line=dict(color='blue')))

# WAU - Utilisateurs Actifs Hebdomadaires
valeurs_wau_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.to_period('W').apply(lambda r: r.start_time)).size()
fig_active_users_filtered.add_trace(go.Scatter(x=valeurs_wau_filtered.index, y=valeurs_wau_filtered, mode='lines', name='WAU', line=dict(color='green')))

# MAU - Utilisateurs Actifs Mensuels
valeurs_mau_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.to_period('M').apply(lambda r: r.start_time)).size()
fig_active_users_filtered.add_trace(go.Scatter(x=valeurs_mau_filtered.index, y=valeurs_mau_filtered, mode='lines', name='MAU', line=dict(color='red')))

fig_active_users_filtered.update_layout(
    title='Utilisateurs Actifs (DAU, WAU, MAU) (Filtrés)',
    xaxis_title='Date',
    yaxis_title='Nombre d\'Utilisateurs',
    legend_title_text='Métriques',
    height=400
)

# Mise à jour du graphique : Engagement des Utilisateurs avec courbes distinctes avec filtres
fig_engagement_users_filtered = go.Figure()

# Utilisateurs Mensuels
valeurs_mensuels_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.to_period('M').apply(lambda r: r.start_time)).size()
fig_engagement_users_filtered.add_trace(go.Scatter(x=valeurs_mensuels_filtered.index, y=valeurs_mensuels_filtered, mode='lines', name='Utilisateurs Mensuels', line=dict(color='red')))

# Utilisateurs Hebdomadaires
valeurs_hebdomadaires_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.to_period('W').apply(lambda r: r.start_time)).size()
fig_engagement_users_filtered.add_trace(go.Scatter(x=valeurs_hebdomadaires_filtered.index, y=valeurs_hebdomadaires_filtered, mode='lines', name='Utilisateurs Hebdomadaires', line=dict(color='green')))

# Utilisateurs Quotidiens
valeurs_quotidiens_filtered = sessions_filtered.groupby(sessions_filtered['session_start'].dt.date).size()
fig_engagement_users_filtered.add_trace(go.Scatter(x=valeurs_quotidiens_filtered.index, y=valeurs_quotidiens_filtered, mode='lines', name='Utilisateurs Quotidiens', line=dict(color='blue')))

# Sessions Moyennes par Utilisateur
fig_engagement_users_filtered.add_trace(go.Scatter(x=valeurs_quotidiens_filtered.index, y=[average_sessions_per_user_filtered] * len(valeurs_quotidiens_filtered.index), mode='lines', name='Sessions Moyennes par Utilisateur', line=dict(color='purple')))

fig_engagement_users_filtered.update_layout(
    title='Engagement des Utilisateurs (Filtré)',
    xaxis_title='Date',
    yaxis_title='Nombre d\'Utilisateurs / Sessions',
    legend_title_text='Métriques',
    height=400
)

# Interface utilisateur Streamlit
st.title('Métriques de l\'Application')

# Onglets pour les métriques
tab1, tab2, tab3, tab4 = st.tabs(["Taux de Conversion", "Utilisateurs Actifs", "Engagement des Utilisateurs", "Durée des Sessions"])

with tab1:
    st.metric(label="Taux de Conversion", value=f"{conversion_rate_filtered:.2f}%")

with tab2:
    st.metric(label="Quotidien (DAU)", value=f"{dau_filtered:.2f}")
    st.metric(label="Hebdomadaire (WAU)", value=f"{wau_filtered:.2f}")
    st.metric(label="Mensuel (MAU)", value=f"{mau_filtered:.2f}")
    st.plotly_chart(fig_active_users_filtered, use_container_width=True)

with tab3:
    st.metric(label="Utilisateurs Quotidiens", value=f"{users_daily_filtered:.2f}")
    st.metric(label="Utilisateurs Hebdomadaires", value=f"{users_weekly_filtered:.2f}")
    st.metric(label="Utilisateurs Mensuels", value=f"{users_monthly_filtered:.2f}")
    st.metric(label="Sessions Moyennes par Utilisateur", value=f"{average_sessions_per_user_filtered:.2f}")
    st.plotly_chart(fig_engagement_users_filtered, use_container_width=True)

with tab4:
    st.metric(label="Durée Moyenne des Sessions (minutes)", value=f"{average_session_duration_minutes_filtered:.2f}")

# Répartition des Utilisateurs par Fréquence d'Utilisation
st.subheader('Répartition des Utilisateurs par Fréquence d\'Utilisation (Filtrée)')
st.plotly_chart(fig_engagement_distribution_filtered, use_container_width=True)

# Pages et fonctionnalités les plus utilisées
st.subheader('Pages et Fonctionnalités les Plus Utilisées')
visited_pages = filtered_sessions['visited_pages'].apply(lambda x: ast.literal_eval(x))
all_visited_pages = [page for sublist in visited_pages for page in sublist]
page_counts = Counter(all_visited_pages)
most_common_pages = page_counts.most_common()
pages_df = pd.DataFrame(most_common_pages, columns=['Page', 'Visites'])
fig_most_common_pages = px.bar(pages_df, x='Visites', y='Page', orientation='h', title='Pages les Plus Visitées')
st.plotly_chart(fig_most_common_pages, use_container_width=True)

# Boutons les plus cliqués
button_pressed_time['time'] = pd.to_datetime(button_pressed_time['time'])
filtered_buttons = button_pressed_time[button_pressed_time['uid'].isin(filtered_users['uid'])]
if date_range:
    filtered_buttons = filtered_buttons[(filtered_buttons['time'] >= pd.Timestamp(start_date)) & (filtered_buttons['time'] <= pd.Timestamp(end_date))]
button_counts = filtered_buttons['button'].value_counts()
button_counts_df = pd.DataFrame(button_counts).reset_index()
button_counts_df.columns = ['Button', 'Presses']
fig_most_common_buttons = px.bar(button_counts_df, x='Presses', y='Button', orientation='h', title='Boutons les Plus Cliqués')
st.plotly_chart(fig_most_common_buttons, use_container_width=True)

# Distribution des durées des sessions (histogramme)
st.subheader('Distribution des Durées des Sessions (minutes)')
fig_session_duration = px.histogram(filtered_sessions, x='session_duration_in_minutes', title='Distribution des Durées des Sessions (minutes)', labels={'session_duration_in_minutes': 'Durée des Sessions (minutes)'})
st.plotly_chart(fig_session_duration, use_container_width=True)

# Fonction de génération de rapport
def generate_report():
    report = f"""
    ## Rapport Automatique

    **Période d'analyse:**
    Toutes les dates disponibles.

    **Métriques Clés:**

    - **Taux de Conversion:** Le taux de conversion, représentant le pourcentage d'utilisateurs ayant effectué une action significative, est de **{conversion_rate_filtered:.2f}%**. Cela signifie que sur l'ensemble des utilisateurs inscrits, environ {conversion_rate_filtered:.2f}% ont réalisé l'action ciblée.
    
    - **Utilisateurs Actifs:**
        - **Quotidien (DAU):** En moyenne, **{dau_filtered:.2f}** utilisateurs sont actifs chaque jour, montrant un engagement constant et régulier.
        - **Hebdomadaire (WAU):** Sur une base hebdomadaire, environ **{wau_filtered:.2f}** utilisateurs se connectent et interagissent avec l'application.
        - **Mensuel (MAU):** **{mau_filtered:.2f}** utilisateurs uniques utilisent l'application chaque mois, indiquant une base d'utilisateurs fidèle sur le long terme.
    
    - **Durée Moyenne des Sessions:** Les sessions durent en moyenne **{average_session_duration_minutes_filtered:.2f} minutes**, ce qui montre un bon niveau d'engagement par session.
    
    - **Engagement des Utilisateurs:**
        - **Nombre Moyen de Sessions par Utilisateur:** Chaque utilisateur participe en moyenne à **{average_sessions_per_user_filtered:.2f}** sessions, ce qui reflète leur engagement avec l'application.
        - **Utilisateurs Quotidiens:** **{users_daily_filtered}** utilisateurs se connectent au moins une fois par jour.
        - **Utilisateurs Hebdomadaires:** **{users_weekly_filtered}** utilisateurs interagissent avec l'application chaque semaine.
        - **Utilisateurs Mensuels:** **{users_monthly_filtered}** utilisateurs actifs chaque mois, démontrant une fidélité continue.

    Ce rapport fournit une vue d'ensemble détaillée de l'engagement et de la fidélité des utilisateurs de l'application Dhoola. En observant les taux de conversion et les métriques d'activité, les décideurs peuvent identifier les points forts et les opportunités d'amélioration pour augmenter l'engagement et la satisfaction des utilisateurs.
    """
    return report

# Fonction pour créer un PDF
def create_pdf(report, filename="rapport.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Ajouter le rapport texte
    for line in report.split('\n'):
        if line.strip() == "":
            pdf.ln(10)  # Add a new line for empty lines
        else:
            pdf.multi_cell(0, 10, txt=line)
    
    # Ajouter les graphiques
    graphs = [
        (fig_engagement_distribution_filtered, "engagement_distribution.png"),
        (fig_active_users_filtered, "active_users.png"),
        (fig_engagement_users_filtered, "engagement_users.png"),
        (fig_most_common_pages, "most_common_pages.png"),
        (fig_most_common_buttons, "most_common_buttons.png"),
        (fig_session_duration, "session_duration.png")
    ]
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        for fig, file_name in graphs:
            img_path = os.path.join(tmpdirname, file_name)
            pio.write_image(fig, img_path, engine="kaleido")
            pdf.add_page()
            pdf.image(img_path, x=10, y=10, w=190)
    
    pdf.output(filename)

# Bouton pour générer le rapport
if st.button('Générer le Rapport'):
    report = generate_report()
    st.markdown(report)
    create_pdf(report)
    with open("rapport.pdf", "rb") as pdf_file:
        st.download_button(label="Télécharger le rapport en PDF", data=pdf_file, file_name="rapport.pdf", mime="application/pdf")