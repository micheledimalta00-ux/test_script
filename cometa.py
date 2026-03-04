import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ==============================
# FUNZIONI DI CALCOLO
# ==============================

def simulate_tfr(ral_list, tfr_percent=0.0833, tasso_rivalut=0.03):
    """Calcola TFR annuo e saldo cumulato"""
    tfr_annuale = [r * tfr_percent for r in ral_list]
    saldo = []
    acc = 0
    for tfr in tfr_annuale:
        acc = acc * (1 + tasso_rivalut) + tfr
        saldo.append(acc)
    return tfr_annuale, saldo

def simulate_cometa(ral_list, contrib_personal, contrib_azienda, growth_rate):
    """Calcola contributi e saldo Cometa annuo"""
    contrib_annuo = []
    saldo = []
    acc = 0
    for r in ral_list:
        total = r * (contrib_personal + contrib_azienda)
        contrib_annuo.append(total)
        acc = acc * (1 + growth_rate) + total
        saldo.append(acc)
    return contrib_annuo, saldo

def prelievo_anticipato(saldo_cometa, perc_prelievo, tassazione):
    """Calcola importo netto prelevabile prima della pensione"""
    prelevabile = [s * perc_prelievo for s in saldo_cometa]
    netto = [p * (1 - tassazione) for p in prelevabile]
    return netto

def generate_ral_list(ral_iniziale, anni, scenario):
    ral_list = []
    ral = ral_iniziale
    for i in range(anni):
        if scenario == "Crescita costante 2%":
            ral *= 1.02
        elif scenario == "Crescita rapida 4%":
            ral *= 1.04
        ral_list.append(ral)
    return ral_list

# ==============================
# STREAMLIT INTERFACCIA
# ==============================

st.set_page_config(page_title="Simulatore TFR vs Fondo Cometa", layout="wide")
st.title("💼 Simulatore Fondo Cometa vs TFR per Metalmeccanici")

# --- Input personali ---
st.sidebar.header("Parametri Personali")
eta_inizio = st.sidebar.number_input("Età attuale", value=26, min_value=18, max_value=70)
eta_pensione = st.sidebar.number_input("Età pensionamento", value=70, min_value=18, max_value=100)
anni_lavoro = eta_pensione - eta_inizio

ral_iniziale = st.sidebar.number_input("RAL iniziale (€)", value=30000)
scenario_ral = st.sidebar.selectbox("Andamento RAL", ["Stabile", "Crescita costante 2%", "Crescita rapida 4%"])

# --- Tassi TFR e Fondo ---
st.sidebar.header("Parametri Fondo e TFR")
comparto_rischio = st.sidebar.selectbox("Comparto rischio Fondo Cometa", ["Basso 2%", "Moderato 4%", "Alto 6%"])
tasso_cometa = {"Basso 2%": 0.02, "Moderato 4%": 0.04, "Alto 6%": 0.06}[comparto_rischio]

contrib_personal = st.sidebar.number_input("Contributo personale (%)", value=2, min_value=0, max_value=20)/100
contrib_azienda = st.sidebar.number_input("Contributo azienda (%)", value=2, min_value=0, max_value=20)/100

tasso_rivalut_tfr = st.sidebar.slider("Rivalutazione TFR annua (%)", min_value=0.0, max_value=10.0, value=3.0)/100
prelievo_anticipato_perc = st.sidebar.slider("Percentuale prelievo anticipato Fondo (%)", min_value=0, max_value=100, value=30)/100
tassazione_prelievo = st.sidebar.slider("Tassazione prelievo (%)", min_value=0, max_value=100, value=23)/100

# --- Generazione RAL annua ---
ral_list = generate_ral_list(ral_iniziale, anni_lavoro, scenario_ral)

# --- Simulazioni ---
tfr_annuo, saldo_tfr = simulate_tfr(ral_list, tfr_percent=0.0833, tasso_rivalut=tasso_rivalut_tfr)
cometa_annuo, saldo_cometa = simulate_cometa(ral_list, contrib_personal, contrib_azienda, tasso_cometa)
netto_prelievo = prelievo_anticipato(saldo_cometa, prelievo_anticipato_perc, tassazione_prelievo)

# --- Creazione DataFrame ---
df = pd.DataFrame({
    "Anno": np.arange(1, anni_lavoro+1),
    "Età": np.arange(eta_inizio+1, eta_pensione+1),
    "RAL (€)": [r for r in ral_list],
    "Acc. TFR annuo (€)": [t for t in tfr_annuo],
    "Saldo TFR (€)": [s for s in saldo_tfr],
    "Contributo Cometa (€)": [c for c in cometa_annuo],
    "Saldo Cometa (€)": [s for s in saldo_cometa],
    "Netto prelievo (€)": [n for n in netto_prelievo]
})

# Forza tutte le colonne numeriche a float
numeric_cols = ["RAL (€)", "Acc. TFR annuo (€)", "Saldo TFR (€)",
                "Contributo Cometa (€)", "Saldo Cometa (€)", "Netto prelievo (€)"]
df[numeric_cols] = df[numeric_cols].astype(float)

st.subheader("📊 Tabella anno per anno")
st.dataframe(df.style.format("{:,.2f}"))

# --- Grafico comparativo ---
st.subheader("📈 Andamento TFR vs Fondo Cometa")
chart = alt.Chart(df).transform_fold(
    ["Saldo TFR (€)", "Saldo Cometa (€)"],
    as_ = ['Tipo', 'Saldo']
).mark_line().encode(
    x=alt.X('Età:Q', title='Età'),
    y=alt.Y('Saldo:Q', title='Saldo (€)'),
    color=alt.Color('Tipo:N', title='Tipo'),
    tooltip=[alt.Tooltip('Età:Q'), alt.Tooltip('Saldo:Q', format=",.2f")]
)
st.altair_chart(chart, use_container_width=True)

st.subheader("💸 Netto prelievo anticipato dal Fondo Cometa")
chart2 = alt.Chart(df).mark_line(color='red').encode(
    x=alt.X('Età:Q', title='Età'),
    y=alt.Y('Netto prelievo (€):Q', title='Netto prelievo (€)'),
    tooltip=[alt.Tooltip('Età:Q'), alt.Tooltip('Netto prelievo (€):Q', format=",.2f")]
)
st.altair_chart(chart2, use_container_width=True)

# --- Metriche finali ---
st.subheader("📌 Metriche finali a pensionamento")
st.markdown(f"- **Saldo TFR finale (€)**: {df['Saldo TFR (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **Saldo Cometa finale (€)**: {df['Saldo Cometa (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **Netto prelievo massimo (%)**: {prelievo_anticipato_perc*100:.0f}% → {df['Netto prelievo (€)'].iloc[-1]:,.2f} €")
st.markdown(f"- **Totale contributi personali (€)**: {df['Contributo Cometa (€)'].sum():,.2f}")
st.markdown(f"- **Rendimento complessivo Fondo Cometa**: {((df['Saldo Cometa (€)'].iloc[-1] - df['Contributo Cometa (€)'].sum())/df['Contributo Cometa (€)'].sum()*100):.2f}%")
st.markdown(f"- **Rendimento complessivo TFR**: {((df['Saldo TFR (€)'].iloc[-1] - df['Acc. TFR annuo (€)'].sum())/df['Acc. TFR annuo (€)'].sum()*100):.2f}%")