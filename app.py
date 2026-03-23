import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────────
# Configuration de la page
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Fraude Financière",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CSS personnalisé
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08); }
    .stMetric label { font-size: 13px !important; color: #666 !important; }
    h1 { color: #1a1a2e; }
    h2, h3 { color: #16213e; }
    .sidebar .stSelectbox label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Chargement et préparation des données
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Dataset.csv")
    df['TransactionStartTime'] = pd.to_datetime(df['TransactionStartTime'])
    df['Heure']        = df['TransactionStartTime'].dt.hour
    df['Jour']         = df['TransactionStartTime'].dt.day
    df['Mois']         = df['TransactionStartTime'].dt.month
    df['JourSemaine']  = df['TransactionStartTime'].dt.day_name()
    df['AmountAbs']    = df['Amount'].abs()
    df['FraudLabel']   = df['FraudResult'].map({0: 'Légitimes', 1: 'Frauduleuses'})
    return df

df = load_data()

# ──────────────────────────────────────────────
# SIDEBAR — Filtres
# ──────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/bank-cards.png", width=60)
st.sidebar.title("🔍 Filtres")

categories = st.sidebar.multiselect(
    "Catégorie de produit",
    options=sorted(df['ProductCategory'].unique()),
    default=sorted(df['ProductCategory'].unique())
)

canaux = st.sidebar.multiselect(
    "Canal",
    options=sorted(df['ChannelId'].unique()),
    default=sorted(df['ChannelId'].unique())
)

heure_range = st.sidebar.slider(
    "Plage horaire",
    min_value=0, max_value=23,
    value=(0, 23)
)

fraude_filtre = st.sidebar.radio(
    "Type de transaction",
    options=["Toutes", "Légitimes uniquement", "Frauduleuses uniquement"]
)

# ──────────────────────────────────────────────
# Filtrage des données
# ──────────────────────────────────────────────
dff = df[
    (df['ProductCategory'].isin(categories)) &
    (df['ChannelId'].isin(canaux)) &
    (df['Heure'] >= heure_range[0]) &
    (df['Heure'] <= heure_range[1])
]

if fraude_filtre == "Légitimes uniquement":
    dff = dff[dff['FraudResult'] == 0]
elif fraude_filtre == "Frauduleuses uniquement":
    dff = dff[dff['FraudResult'] == 1]

# ──────────────────────────────────────────────
# EN-TÊTE
# ──────────────────────────────────────────────
st.title("💳 Dashboard — Détection de Fraude Financière")
st.markdown(f"**Dataset :** Transactions e-commerce · **Données filtrées :** {len(dff):,} / {len(df):,} transactions")
st.markdown("---")

# ──────────────────────────────────────────────
# KPI METRICS
# ──────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

nb_transactions  = len(dff)
nb_fraudes       = dff['FraudResult'].sum()
taux_fraude      = (nb_fraudes / nb_transactions * 100) if nb_transactions > 0 else 0
montant_total    = dff['AmountAbs'].sum()
montant_moyen    = dff['AmountAbs'].mean()

col1.metric("📦 Transactions", f"{nb_transactions:,}")
col2.metric("🚨 Fraudes détectées", f"{nb_fraudes}")
col3.metric("⚠️ Taux de fraude", f"{taux_fraude:.2f}%")
col4.metric("💰 Volume total", f"{montant_total:,.0f}")
col5.metric("📊 Montant moyen", f"{montant_moyen:,.0f}")

st.markdown("---")

# ──────────────────────────────────────────────
# LIGNE 1 : Distribution catégories + Camembert fraude
# ──────────────────────────────────────────────
col_a, col_b = st.columns([2, 1])

with col_a:
    st.subheader("📂 Transactions par catégorie de produit")
    cat_data = dff['ProductCategory'].value_counts().reset_index()
    cat_data.columns = ['Catégorie', 'Nombre']
    fig_cat = px.bar(
        cat_data, x='Nombre', y='Catégorie', orientation='h',
        color='Nombre', color_continuous_scale='Blues',
        template='plotly_white'
    )
    fig_cat.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0),
                          coloraxis_showscale=False)
    st.plotly_chart(fig_cat, use_container_width=True)

with col_b:
    st.subheader("🔴 Répartition des fraudes")
    fraud_data = dff['FraudLabel'].value_counts().reset_index()
    fraud_data.columns = ['Type', 'Nombre']
    fig_pie = px.pie(
        fraud_data, names='Type', values='Nombre',
        color='Type',
        color_discrete_map={'Légitimes': '#2ecc71', 'Frauduleuses': '#e74c3c'},
        hole=0.4, template='plotly_white'
    )
    fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# ──────────────────────────────────────────────
# LIGNE 2 : Volume horaire + Scatter Amount vs Value
# ──────────────────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("⏰ Volume de transactions par heure")
    hourly = dff.groupby(['Heure', 'FraudLabel']).size().reset_index(name='Nb')
    fig_hour = px.bar(
        hourly, x='Heure', y='Nb', color='FraudLabel',
        color_discrete_map={'Légitimes': '#3498db', 'Frauduleuses': '#e74c3c'},
        barmode='stack', template='plotly_white'
    )
    fig_hour.update_layout(margin=dict(l=0, r=0, t=20, b=0),
                           xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig_hour, use_container_width=True)

with col_d:
    st.subheader("💹 Montant vs Valeur (par catégorie)")
    fig_scatter = px.scatter(
        dff, x='AmountAbs', y='Value',
        color='ProductCategory',
        size='AmountAbs', size_max=20,
        hover_data=['ChannelId', 'FraudLabel'],
        log_x=True, log_y=True,
        template='plotly_white'
    )
    fig_scatter.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ──────────────────────────────────────────────
# LIGNE 3 : Boxplot montants + Sunburst
# ──────────────────────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("📦 Distribution des montants par canal")
    fig_box = px.box(
        dff, x='ChannelId', y='AmountAbs', color='ChannelId',
        log_y=True, points='outliers', template='plotly_white'
    )
    fig_box.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_box, use_container_width=True)

with col_f:
    st.subheader("🌐 Répartition hiérarchique")
    fig_sun = px.sunburst(
        dff, path=['ProductCategory', 'ChannelId', 'FraudLabel'],
        template='plotly_white'
    )
    fig_sun.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_sun, use_container_width=True)

# ──────────────────────────────────────────────
# LIGNE 4 : Évolution temporelle
# ──────────────────────────────────────────────
st.subheader("📈 Évolution horaire des transactions")
dff_time = dff.copy()
dff_time['Date'] = dff_time['TransactionStartTime'].dt.floor('h')
timeline = dff_time.groupby(['Date', 'FraudLabel']).size().reset_index(name='Nb')
fig_line = px.line(
    timeline, x='Date', y='Nb', color='FraudLabel',
    color_discrete_map={'Légitimes': '#2ecc71', 'Frauduleuses': '#e74c3c'},
    markers=True, template='plotly_white'
)
fig_line.update_layout(margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig_line, use_container_width=True)

# ──────────────────────────────────────────────
# TABLEAU DE DONNÉES FILTRÉES
# ──────────────────────────────────────────────
with st.expander("📋 Voir les données filtrées"):
    st.dataframe(
        dff[['ProductId', 'ProductCategory', 'ChannelId', 'Amount',
             'Value', 'TransactionStartTime', 'PricingStrategy', 'FraudLabel']]
        .reset_index(drop=True),
        use_container_width=True,
        height=300
    )
    st.download_button(
        label="⬇️ Télécharger les données filtrées (CSV)",
        data=dff.to_csv(index=False).encode('utf-8'),
        file_name="transactions_filtrees.csv",
        mime="text/csv"
    )

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#999; font-size:13px;'>"
    "Dashboard réalisé dans le cadre du Projet Final · Master Finance Digitale"
    "</p>",
    unsafe_allow_html=True
)
