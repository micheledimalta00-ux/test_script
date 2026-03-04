import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Simulatore Fondo Cometa vs TFR", layout="wide")

st.title("Simulatore Fondo Cometa vs TFR")

# ==============================
# INPUT UTENTE
# ==============================
eta = st.number_input("Età attuale", min_value=18, max_value=70, value=26)
eta_pensione = st.number_input("Età pensione prevista", min_value=60, max_value=75, value=70)
anni_lavoro = eta_pensione - eta

# Andamento RAL
st.subheader("Andamento RAL negli anni")
ral_mode = st.selectbox("Scenario RAL", ["Costante", "Lineare Crescente", "Non Lineare Crescente"])
ral_iniziale = st.number_input("RAL Iniziale (€)", value=30000)

# Contributo aggiuntivo azienda
contrib_azienda = st.number_input("Quota aggiuntiva azienda (%)", value=2.0) / 100
contrib_personale = st.number_input("Quota versamento personale (%)", value=6.0) / 100

# Tassazioni
tassazione_pensione = st.number_input("Tassazione ritiro pensione (%)", value=15.0) / 100
tassazione_pre_pensione = st.number_input("Tassazione ritiro anticipato (%)", value=23.0) / 100

# Rischio comparti (fondo cometa)
comparti = {
    "Basso": {"tasso_medio": 0.02, "volatilita": 0.01},
    "Moderato": {"tasso_medio": 0.035, "volatilita": 0.02},
    "Alto": {"tasso_medio": 0.05, "volatilita": 0.04},
}
comparto_scelto = st.selectbox("Comparto fondo Cometa", list(comparti.keys()))

# ==============================
# GENERA SCENARI
# ==============================
def genera_ral(anni, start, mode):
    ral = []
    for i in range(anni):
        t = i / max(1, anni-1)
        if mode == "Costante":
            val = start
        elif mode == "Lineare Crescente":
            val = start * (1 + 0.02 * t * anni)
        elif mode == "Non Lineare Crescente":
            val = start * (1 + 0.03 * t**2 * anni)
        ral.append(float(val))
    return ral

def genera_fondo_cometa(ral, contrib_pers, contrib_az, tasso, vol):
    saldo, vers_lordo, vers_netto = [], [], []
    tot = 0
    for r in ral:
        vers = r * contrib_pers
        azi = r * contrib_az
        tot += (vers + azi) * (1 + np.random.normal(tasso, vol))
        saldo.append(float(tot))
        vers_lordo.append(float(vers + azi))
        vers_netto.append(float((vers + azi)*(1-tassazione_pensione)))
    return saldo, vers_lordo, vers_netto

def genera_tfr(ral, contrib=0.075):
    saldo, vers_lordo, vers_netto = [], [], []
    tot = 0
    for r in ral:
        vers = r * contrib
        tot += vers
        saldo.append(float(tot))
        vers_lordo.append(float(vers))
        vers_netto.append(float(vers*(1-tassazione_pensione)))
    return saldo, vers_lordo, vers_netto

# ==============================
# CALCOLI
# ==============================
ral_list = genera_ral(anni_lavoro, ral_iniziale, ral_mode)
fondo = {}
tfr = {}

tasso_medio = comparti[comparto_scelto]["tasso_medio"]
vol = comparti[comparto_scelto]["volatilita"]

fondo["Saldo Netto"], fondo["Contrib Totale Lordo"], fondo["Contrib Totale Netto"] = genera_fondo_cometa(
    ral_list, contrib_personale, contrib_azienda, tasso_medio, vol
)
tfr["Saldo Netto"], tfr["Contrib Totale Lordo"], tfr["Contrib Totale Netto"] = genera_tfr(ral_list)

df = pd.DataFrame({
    "Anno": list(range(1, anni_lavoro+1)),
    "RAL (€)": ral_list,
    "Fondo Cometa Netto (€)": fondo["Saldo Netto"],
    "Fondo Cometa Lordo (€)": fondo["Contrib Totale Lordo"],
    "TFR Netto (€)": tfr["Saldo Netto"],
    "TFR Lordo (€)": tfr["Contrib Totale Lordo"],
    "Differenza Cometa vs TFR (€)": [f-t for f,t in zip(fondo["Saldo Netto"], tfr["Saldo Netto"])]
})

# ==============================
# TABELLONE
# ==============================
st.subheader("Tabella riepilogativa")
st.dataframe(df)

# ==============================
# GRAFICI
# ==============================
st.subheader("Grafici evoluzione")
metriche = [
    ("RAL", "RAL (€)"),
    ("Fondo Cometa Netto", "Fondo Cometa Netto (€)"),
    ("Fondo Cometa Lordo", "Fondo Cometa Lordo (€)"),
    ("TFR Netto", "TFR Netto (€)"),
    ("TFR Lordo", "TFR Lordo (€)"),
    ("Differenza Cometa vs TFR", "Differenza Cometa vs TFR (€)")
]

for titolo, col in metriche:
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("Anno", title="Anno di lavoro"),
        y=alt.Y(col, title=titolo),
        tooltip=["Anno", col]
    ).properties(title=titolo)
    st.altair_chart(chart, use_container_width=True)