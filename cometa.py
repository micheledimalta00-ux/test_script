# simulatore_cometa_dettagliato.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ==============================
# FUNZIONI FINANZIARIE
# ==============================
def annual_fondo_schedule(ral_list, contrib_lav_perc, contrib_az_perc, rates, tax_return, tax_exit, prelievo_anticipato=False):
    balances_lordo, balances_netto = [], []
    contrib_lav_lordo_list, contrib_az_lordo_list = [], []
    contrib_lav_netto_list, contrib_az_netto_list = [], []
    saldo = 0
    for i in range(len(ral_list)):
        ral = ral_list[i]
        # contributi annui lordi
        c_lav = ral * contrib_lav_perc / 100
        c_az = ral * contrib_az_perc / 100
        contrib_lav_lordo_list.append(c_lav)
        contrib_az_lordo_list.append(c_az)
        
        # aggiungiamo al saldo
        saldo += c_lav + c_az
        
        # rendimento lordo
        r = rates[i]
        rend_lordo = saldo * r
        
        # tasse annuali sul rendimento
        rend_netto = rend_lordo * (1 - tax_return)
        saldo_netto = saldo + rend_netto
        
        # se prelievo anticipato, applica tassa in uscita sul saldo netto
        if prelievo_anticipato:
            saldo_netto *= (1 - tax_exit)
        
        # registriamo saldo
        balances_lordo.append(saldo + rend_lordo)
        balances_netto.append(saldo_netto)
        
        # contributi netti
        contrib_lav_netto_list.append(c_lav)
        contrib_az_netto_list.append(c_az)
        
        saldo = saldo_netto  # saldo netto per anno successivo
    
    return {
        "Saldo Lordo": balances_lordo,
        "Saldo Netto": balances_netto,
        "Contrib Lavoratore Lordo": contrib_lav_lordo_list,
        "Contrib Azienda Lordo": contrib_az_lordo_list,
        "Contrib Lavoratore Netto": contrib_lav_netto_list,
        "Contrib Azienda Netto": contrib_az_netto_list,
    }

def annual_tfr_schedule(ral_list, inflations, tax_exit, prelievo_anticipato=False):
    balances_lordo, balances_netto = [], []
    contrib_list = []
    tfr = 0
    for i in range(len(ral_list)):
        ral = ral_list[i]
        c = ral * 0.076  # quota TFR annua
        contrib_list.append(c)
        tfr += c
        tfr_lordo = tfr * (1 + 0.015 + 0.75 * inflations[i])
        tfr_netto = tfr_lordo * (1 - tax_exit) if prelievo_anticipato else tfr_lordo
        balances_lordo.append(tfr_lordo)
        balances_netto.append(tfr_netto)
    return balances_lordo, balances_netto, contrib_list

# ==============================
# SCENARI COMPARTO
# ==============================
COMPARTI = {
    "Monetario Plus (~3% medio)": 0.031,
    "Reddito (~5.5% medio)": 0.055,
    "Crescita (~10.4% medio)": 0.104,
}

TAX_RETURN = 0.20
TAX_EXIT = 0.15  # aliquota uscita fondi/pensioni

# ==============================
# STREAMLIT APP
# ==============================
st.set_page_config(page_title="Simulatore Fondo Cometa vs TFR Dettagliato", layout="wide")
st.title("Simulatore Fondo Cometa vs TFR Aziendale - Dettagliato")

# ------------------------------
# INPUT
# ------------------------------
with st.sidebar:
    st.header("Dati Personali")
    eta = st.number_input("Età attuale", 18, 70, 26)
    pensione = st.number_input("Età pensione prevista", 18, 70, 70)
    
    st.header("RAL / Contributi")
    ral_base = st.number_input("RAL base (€)", value=30000)
    anni_lavoro = pensione - eta
    st.markdown(f"Simulazione su {anni_lavoro} anni")
    
    contrib_lav_perc = st.slider("Contributo lavoratore (%)", 0.0, 10.0, 1.2)
    contrib_az_perc = st.slider("Contributo azienda (%)", 0.0, 10.0, 2.0)
    
    st.header("Comparto Fondo")
    comparto = st.selectbox("Scelta comparto", list(COMPARTI.keys()))
    
    st.header("Inflazione / Tassazione")
    inflazione_media = st.slider("Inflazione media (%)", 0.0, 10.0, 2.0) / 100
    tax_return = st.slider("Tassazione rendimento (%)", 0, 50, 20) / 100
    tax_exit = st.slider("Tassazione prelievo (%)", 0, 50, 15) / 100
    
    st.header("RAL anno per anno (opzionale)")
    st.markdown("Se vuoi simulare aumenti RAL diversi ogni anno, inserisci una lista separata da virgola")
    ral_input = st.text_input("RAL per anno", value=",".join([str(ral_base)] * anni_lavoro))
    
    prelievo_anticipato = st.checkbox("Considera prelievo anticipato con tassazione", value=False)

# ------------------------------
# PREPARAZIONE DATI
# ------------------------------
try:
    ral_list = [float(x) for x in ral_input.split(",")]
    if len(ral_list) != anni_lavoro:
        ral_list = [ral_base]*anni_lavoro
except:
    ral_list = [ral_base]*anni_lavoro

rates_fondo = [COMPARTI[comparto]] * anni_lavoro
inflations = [inflazione_media] * anni_lavoro

# ------------------------------
# CALCOLI
# ------------------------------
fondo = annual_fondo_schedule(
    ral_list,
    contrib_lav_perc,
    contrib_az_perc,
    rates_fondo,
    tax_return,
    tax_exit,
    prelievo_anticipato
)

tfr_lordo, tfr_netto, tfr_contrib = annual_tfr_schedule(
    ral_list, inflations, tax_exit, prelievo_anticipato
)

# ------------------------------
# TABELLA DETTAGLIATA
# ------------------------------
df = pd.DataFrame({
    "Anno": np.arange(1, anni_lavoro + 1),
    "RAL (€)": ral_list,
    "Saldo Fondo Lordo (€)": fondo["Saldo Lordo"],
    "Saldo Fondo Netto (€)": fondo["Saldo Netto"],
    "Contrib Lavoratore Lordo (€)": fondo["Contrib Lavoratore Lordo"],
    "Contrib Azienda Lordo (€)": fondo["Contrib Azienda Lordo"],
    "Contrib Lavoratore Netto (€)": fondo["Contrib Lavoratore Netto"],
    "Contrib Azienda Netto (€)": fondo["Contrib Azienda Netto"],
    "Saldo TFR Lordo (€)": tfr_lordo,
    "Saldo TFR Netto (€)": tfr_netto,
    "Contributo TFR (€)": tfr_contrib,
})

st.subheader("Tabella Valori Anno per Anno")
st.dataframe(df)

# ------------------------------
# GRAFICI COMPARATIVI
# ------------------------------
st.subheader("Grafici Comparativi")
metriche_grafici = [
    ("Saldo Fondo Lordo (€)", "Saldo Fondo Lordo (€)"),
    ("Saldo Fondo Netto (€)", "Saldo Fondo Netto (€)"),
    ("Saldo TFR Lordo (€)", "Saldo TFR Lordo (€)"),
    ("Saldo TFR Netto (€)", "Saldo TFR Netto (€)"),
    ("Differenza Cometa vs TFR (€)", "Saldo Fondo Netto (€) - Saldo TFR Netto (€)"),
    ("Contributi Totali Fondo (€)", "Contrib Lavoratore Netto (€) + Contrib Azienda Netto (€)"),
]

df["Differenza Cometa vs TFR (€)"] = np.array(fondo["Saldo Netto"]) - np.array(tfr_netto)
df["Contributi Totali Fondo (€)"] = np.array(fondo["Contrib Lavoratore Netto"]) + np.array(fondo["Contrib Azienda Netto"])

for title, col in metriche_grafici:
    chart = alt.Chart(df).mark_line(point=True).encode(
        x="Anno",
        y=col,
        tooltip=["Anno", col]
    ).properties(title=title)
    st.altair_chart(chart, use_container_width=True)