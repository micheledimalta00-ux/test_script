import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ==============================
# FUNZIONI DI CALCOLO
# ==============================

def simulate_tfr(ral_list, tfr_percent=0.0833, tasso_rivalut=0.03):
    """Calcola TFR annuo e saldo cumulato"""
    tfr_annuale = [r * tfr_percent for r in ral_list]  # circa 1 mensilità
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
        # "Stabile" lascia invariata
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
    "RAL (€)": [round(r,0) for r in ral_list],
    "Acc. TFR annuo (€)": [round(t,2) for t in tfr_annuo],
    "Saldo TFR (€)": [round(s,2) for s in saldo_tfr],
    "Contributo Cometa (€)": [round(c,2) for c in cometa_annuo],
    "Saldo Cometa (€)": [round(s,2) for s in saldo_cometa],
    "Netto prelievo (€)": [round(n,2) for n in netto_prelievo]
})

st.subheader("📊 Tabella anno per anno")
st.dataframe(df.style.format({"RAL (€)":"{:.0f}", "Acc. TFR annuo (€)":"{:.2f}",
                              "Saldo TFR (€)":"{:.2f}", "Contributo Cometa (€)":"{:.2f}",
                              "Saldo Cometa (€)":"{:.2f}", "Netto prelievo (€)":"{:.2f}"}))

# --- Grafico comparativo ---
st.subheader("📈 Andamento TFR vs Fondo Cometa")
chart = alt.Chart(df).transform_fold(
    ["Saldo TFR (€)", "Saldo Cometa (€)"],
    as_ = ['Tipo', 'Saldo']
).mark_line().encode(
    x='Età',
    y='Saldo',
    color='Tipo',
    tooltip=['Età', 'Saldo']
)
st.altair_chart(chart, use_container_width=True)

st.subheader("💸 Netto prelievo anticipato dal Fondo Cometa")
chart2 = alt.Chart(df).mark_line(color='red').encode(
    x='Età',
    y='Netto prelievo (€)',
    tooltip=['Età', 'Netto prelievo (€)']
)
st.altair_chart(chart2, use_container_width=True)

# --- Metriche finali ---
st.subheader("📌 Metriche finali a pensionamento")
st.markdown(f"- **Saldo TFR finale (€)**: {round(saldo_tfr[-1],2)}")
st.markdown(f"- **Saldo Cometa finale (€)**: {round(saldo_cometa[-1],2)}")
st.markdown(f"- **Netto prelievo massimo (%)**: {prelievo_anticipato_perc*100}% → {round(netto_prelievo[-1],2)} €")
st.markdown(f"- **Totale contributi personali (€)**: {round(sum(cometa_annuo),2)}")
st.markdown(f"- **Rendimento complessivo Fondo Cometa**: {round((saldo_cometa[-1] - sum(cometa_annuo))/sum(cometa_annuo)*100,2)}%")
st.markdown(f"- **Rendimento complessivo TFR**: {round((saldo_tfr[-1] - sum(tfr_annuo))/sum(tfr_annuo)*100,2)}%")