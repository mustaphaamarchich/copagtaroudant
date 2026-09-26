import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="COPAG Logistics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_FILE = Path("copag_logistics.csv")
PASSWORD = "taroudant.copag"

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #666;
        margin-bottom: 1.5rem;
    }
    .login-box {
        max-width: 520px;
        margin: 80px auto 0 auto;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #ddd;
        box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# AUTHENTIFICATION
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("# 🚚 COPAG Logistics")
    st.markdown("### Plateforme d'analyse logistique")
    st.write("Veuillez saisir le mot de passe pour accéder au tableau de bord.")

    password = st.text_input(
        "Mot de passe",
        type="password",
        placeholder="Entrez le mot de passe"
    )

    if st.button("🔐 Se connecter", use_container_width=True):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect.")

    st.caption("COPAG — Analyse des données logistiques")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        return None
    data = pd.read_csv(DATA_FILE)

    # Conversion automatique des dates lorsque possible
    for col in data.columns:
        if any(word in col.lower() for word in ["date", "day", "datetime"]):
            try:
                data[col] = pd.to_datetime(data[col])
            except Exception:
                pass

    return data

df = load_data()

if df is None:
    st.error("Le fichier copag_logistics.csv est introuvable.")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚚 COPAG Logistics")
st.sidebar.caption("Tableau de bord logistique")

if st.sidebar.button("🔒 Déconnexion", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Filtres")

filtered = df.copy()

# Filtres automatiques pour les colonnes catégorielles
categorical_cols = [
    c for c in df.columns
    if df[c].dtype == "object" and 1 < df[c].nunique() <= 50
]

for col in categorical_cols[:8]:
    options = sorted(df[col].dropna().astype(str).unique().tolist())
    selected = st.sidebar.multiselect(
        col.replace("_", " ").title(),
        options,
        default=options
    )
    if selected:
        filtered = filtered[filtered[col].astype(str).isin(selected)]

# ============================================================
# TITRE
# ============================================================
st.markdown('<div class="main-title">🚚 COPAG — Analyse Logistique</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Tableau de bord interactif pour le suivi et l’analyse des opérations logistiques.</div>',
    unsafe_allow_html=True
)

# ============================================================
# KPI
# ============================================================
st.subheader("📊 Indicateurs clés")

numeric_cols = filtered.select_dtypes(include="number").columns.tolist()

# KPI génériques robustes au dataset
kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.metric("📦 Nombre d'enregistrements", f"{len(filtered):,}")

# KPI métier si présents dans le dataset
with kpi_cols[1]:
    if "on_time" in filtered.columns:
        rate = filtered["on_time"].mean() * 100
        st.metric("⏱️ Livraisons à l'heure", f"{rate:.1f}%")
    else:
        st.metric("🔢 Variables numériques", len(numeric_cols))

with kpi_cols[2]:
    if "delay_min" in filtered.columns:
        st.metric("⏳ Retard moyen", f"{filtered['delay_min'].mean():.1f} min")
    elif "cost_mad" in filtered.columns:
        st.metric("💰 Coût moyen", f"{filtered['cost_mad'].mean():,.2f} MAD")
    else:
        st.metric("📈 Colonnes", len(filtered.columns))

with kpi_cols[3]:
    if "cost_mad" in filtered.columns:
        st.metric("💰 Coût total", f"{filtered['cost_mad'].sum():,.0f} MAD")
    elif numeric_cols:
        col = numeric_cols[0]
        st.metric(f"Σ {col}", f"{filtered[col].sum():,.2f}")
    else:
        st.metric("Données", "Disponibles")

# ============================================================
# ANALYSES
# ============================================================
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Vue générale",
    "🚛 Analyse logistique",
    "🌱 Coûts & environnement",
    "📋 Données"
])

with tab1:
    st.subheader("Vue générale")

    if numeric_cols:
        selected_num = st.selectbox(
            "Choisir une variable numérique",
            numeric_cols
        )

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(filtered[selected_num].dropna(), bins=30)
        ax.set_title(f"Distribution de {selected_num}")
        ax.set_xlabel(selected_num)
        ax.set_ylabel("Fréquence")
        ax.grid(alpha=0.25)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Aucune variable numérique disponible pour cette analyse.")

with tab2:
    st.subheader("🚛 Analyse des opérations logistiques")

    if "delay_min" in filtered.columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(filtered["delay_min"].dropna(), bins=30)
        ax.set_title("Distribution des retards")
        ax.set_xlabel("Retard (minutes)")
        ax.set_ylabel("Nombre d'expéditions")
        ax.grid(alpha=0.25)
        st.pyplot(fig)
        plt.close(fig)

    if "transport_mode" in filtered.columns:
        mode_stats = (
            filtered.groupby("transport_mode")
            .size()
            .sort_values(ascending=False)
        )
        st.write("### Expéditions par mode de transport")
        st.bar_chart(mode_stats)

    if "region" in filtered.columns and "delay_min" in filtered.columns:
        region_delay = (
            filtered.groupby("region")["delay_min"]
            .mean()
            .sort_values(ascending=False)
        )
        st.write("### Retard moyen par région")
        st.bar_chart(region_delay)

with tab3:
    st.subheader("🌱 Coûts et environnement")

    if "cost_mad" in filtered.columns:
        st.metric(
            "Coût moyen par expédition",
            f"{filtered['cost_mad'].mean():,.2f} MAD"
        )

    if "co2_kg" in filtered.columns:
        st.metric(
            "Émissions CO₂ totales",
            f"{filtered['co2_kg'].sum():,.2f} kg"
        )

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.hist(filtered["co2_kg"].dropna(), bins=30)
        ax.set_title("Distribution des émissions CO₂")
        ax.set_xlabel("CO₂ (kg)")
        ax.set_ylabel("Nombre d'expéditions")
        ax.grid(alpha=0.25)
        st.pyplot(fig)
        plt.close(fig)

    if "fuel_liters" in filtered.columns:
        st.metric(
            "Consommation moyenne",
            f"{filtered['fuel_liters'].mean():,.2f} L"
        )

with tab4:
    st.subheader("📋 Exploration des données")
    st.write(f"**{len(filtered):,} lignes × {len(filtered.columns)} colonnes**")
    st.dataframe(filtered, use_container_width=True)

    csv_download = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger les données filtrées",
        data=csv_download,
        file_name="copag_logistics_filtre.csv",
        mime="text/csv"
    )

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("COPAG Logistics • Application Streamlit d'analyse des données logistiques")
