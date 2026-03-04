# simulatore_cometa.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ==============================
# FUNZIONI CALCOLO FINANZIARIO
# ==============================

def annual_mutuo_schedule(principal, rates, contributions, years, tax_rate):
    """Calcola anno per anno saldo fondo con rendimento netto."""
    balances = []
    saved = 0
    for i in range(years):
        r = rates[i]
        # contributo anno i
        saved += contributions[i]
        # rendimento lordo su saldo
        gross_return = saved * r
        # tassazione sui rendimenti
        net_return = gross_return * (1 - tax_rate)
        saved += net_return
        balances.append(saved)
    return balances

def annual_tfr_schedule(initial_tfr, inflations, years):
    """Calcolo TFR anno per anno secondo rivalutazione normativa."""
    balances = []
    tfr = initial_tfr
    for i in range(years):
        # rivalutazione = 1,5% + 75% inflazione
        tfr = tfr * (1 + 0.015 + 0.75 * inflations[i])
        balances.append(tfr)
    return balances

# ==============================
# DATI PREDEFINITI SCENARI
# ==============================

COMPARTI = {
    "Monetario Plus (~3% medio)": 0.031,
    "Reddito (~5.5% medio)": 0.055,
    "Crescita (~10.4% medio)": 0.104,
}

TAX_RENDIMENTO = 0.20  # percentuale tassa sui rendimenti del fondo
TAX_USCITA_BASE = 0.15  # aliquota base in uscita dalla pensione

# ==============================
# STREAMLIT APP
# ==============================

st.set_page_config(page_title="Simulatore Fondo Cometa vs TFR", layout="wide")
st.title("Simulatore Fondo Pensione Cometa vs TFR Aziendale")

# ------------------------------
# INPUT IN SIDEBAR
# ------------------------------
with st.sidebar:

    st.header("Parametri Personali")

    eta = st.number_input("Età attuale", min_value=18, max_value=70, value=26)
    pensione = st.number_input("Età pensione prevista", min_value=18, max_value=70, value=70)

    ral = st.number_input("RAL annua (€)", value=30000)
    contrib_lav = st.slider("Contributo lavoratore (% RAL)", 0.0, 10.0, 1.2)
    contrib_azienda = st.slider("Contributo azienda (% RAL)", 0.0, 10.0, 2.0)

    comparto = st.selectbox("Comparto del Fondo Cometa", list(COMPARTI.keys()))

    st.markdown("---")

    st.header("Parametri Economici")
    inflazione_media = st.slider("Inflazione media attesa (%)", 0.0, 10.0, 2.0) / 100

# ------------------------------
# SETUP ANNI
# ------------------------------
anni_lavoro = pensione - eta
years = anni_lavoro if anni_lavoro > 0 else 0

# generazione tassi annuali dello scenario
base_return = COMPARTI[comparto]
rates_fondo = [base_return] * years

# inflazione costante
inflations = [inflazione_media] * years

# contributi anno per anno
contrib_annuali = [(ral * (contrib_lav + contrib_azienda) / 100) for _ in range(years)]

# ==============================
# CALCOLO ANNO PER ANNO
# ==============================
fondo_balances = annual_mutuo_schedule(
    principal=0,
    rates=rates_fondo,
    contributions=contrib_annuali,
    years=years,
    tax_rate=TAX_RENDIMENTO
)

# TFR
initial_tfr = ral * 0.076  # quota TFR maturata stimata
tfr_balances = annual_tfr_schedule(initial_tfr, inflations, years)

# ==============================
# PREPARAZIONE DATI TABELLA
# ==============================

df = pd.DataFrame({
    "Anno": np.arange(1, years + 1),
    "Saldo Fondo Cometa (€)": fondo_balances,
    "Saldo TFR (€)": tfr_balances,
    "Rendimento Netto Fondo (%)": [base_return * 100] * years,
    "Contributi Versati (€)": contrib_annuali,
})

st.subheader("Tabella Valori Anno per Anno")
st.dataframe(df)

# ==============================
# CALCOLO METRICHE
# ==============================

# metriche per grafici
saldo_cometa = np.array(fondo_balances)
saldo_tfr = np.array(tfr_balances)
diff_balances = saldo_cometa - saldo_tfr

metrics = {
    "Saldo Fondo Cometa": saldo_cometa,
    "Saldo TFR Aziendale": saldo_tfr,
    "Differenza Cometa vs TFR": diff_balances,
    "Contributi Totali Accumulati": np.cumsum(contrib_annuali),
    "Rendimento Netto (% annuo)": [base_return * 100] * years,
    "Guadagno Net vs TFR (€)": diff_balances,
}

# ==============================
# GRAFICI
# ==============================

st.subheader("Grafici Comparativi")

for title, values in metrics.items():
    chart_data = pd.DataFrame({
        "Anno": np.arange(1, years + 1),
        title: values
    })
    chart = alt.Chart(chart_data).mark_line(point=True).encode(
        x="Anno",
        y=title,
        tooltip=["Anno", title]
    ).properties(
        title=title
    )
    st.altair_chart(chart, use_container_width=True)