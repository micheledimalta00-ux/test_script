import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Simulatore Avanzato TFR vs Cometa", layout="wide")
st.title("💼 Simulatore Avanzato TFR vs Fondo Cometa (Legge 2026)")

# ==============================
# HELP E DESCRIZIONI
# ==============================
prelievo_help = """Per legge puoi ottenere:
- 75% del montante per spese sanitarie gravi (qualsiasi anno)
- 75% per acquisto/ristrutturazione prima casa (dopo 8 anni)
- 30% per ulteriori esigenze personali (dopo 8 anni)
Non puoi superare questi limiti."""
tassazione_help = """- Spese sanitarie: aliquota agevolata 9-15%
- Casa/altre esigenze: tassazione standard ~23%"""
strategia_help = """Strategie finanziarie predefinite: combinazioni di contributo personale, contributo azienda, profilo rischio (rendimento atteso fondo)"""
ral_help = """10 scenari possibili di crescita RAL fino alla pensione: da stabile a crescita rapida"""
contrib_extra_help = """Contributo volontario aggiuntivo per sbloccare il contributo aziendale gratuito e massimizzare deducibilità fiscale (€5.300/anno max)"""

# ==============================
# INPUT UTENTE
# ==============================
st.sidebar.header("Parametri Personali")
eta_inizio = st.sidebar.number_input("Età attuale", value=26, min_value=18, max_value=70, help="Età del lavoratore")
eta_pensione = st.sidebar.number_input("Età pensionamento", value=70, min_value=18, max_value=100, help="Età alla pensione")
anni_lavoro = eta_pensione - eta_inizio

st.sidebar.header("RAL e Strategie")
ral_iniziale = st.sidebar.number_input("RAL iniziale (€)", value=30000, help="Reddito annuo lordo iniziale")
scenario_ral = st.sidebar.selectbox("Andamento RAL", 
                                    ["Stabile","Crescita 1%","Crescita 2%","Crescita 3%","Crescita 4%","Fluttuante bassa","Fluttuante media","Fluttuante alta","Crescita accelerata","Crescita decrescente"],
                                    help=ral_help)

strategia = st.sidebar.selectbox("Strategia finanziaria (predefinita)", 
                                 ["Conservativa","Moderata","Bilanciata","Aggressiva","Massimo contributo","Minimo contributo","Equilibrata"],
                                 help=strategia_help)

contrib_extra = st.sidebar.number_input("Contributo volontario extra (%)", value=0, min_value=0, max_value=10, help=contrib_extra_help)

st.sidebar.header("Tipologia Prelievo")
tipo_prelievo = st.sidebar.selectbox("Prelievo legale consentito", ["Spese sanitarie","Prima casa","Ulteriori esigenze"], help=prelievo_help)

# ==============================
# PARAMETRI BASE STRATEGIE FINANZIARIE
# ==============================
strategies = {
    "Conservativa": {"personale":0.02,"azienda":0.02,"rendimento":0.02},
    "Moderata": {"personale":0.03,"azienda":0.02,"rendimento":0.04},
    "Bilanciata": {"personale":0.04,"azienda":0.03,"rendimento":0.05},
    "Aggressiva": {"personale":0.05,"azienda":0.03,"rendimento":0.06},
    "Massimo contributo": {"personale":0.053,"azienda":0.03,"rendimento":0.05},
    "Minimo contributo": {"personale":0.01,"azienda":0.02,"rendimento":0.03},
    "Equilibrata": {"personale":0.025,"azienda":0.025,"rendimento":0.045},
}

sel_strategy = strategies[strategia]
contrib_personal = sel_strategy["personale"] + contrib_extra/100
contrib_azienda = sel_strategy["azienda"]
tasso_cometa = sel_strategy["rendimento"]
tasso_rivalut_tfr = 0.03  # Rivalutazione TFR fissa media

# ==============================
# GENERAZIONE RAL
# ==============================
def generate_ral(ral_base, anni, scenario):
    ral_list = []
    ral = ral_base
    for i in range(anni):
        if scenario=="Stabile": ral_list.append(ral)
        elif scenario=="Crescita 1%": ral *= 1.01; ral_list.append(ral)
        elif scenario=="Crescita 2%": ral *= 1.02; ral_list.append(ral)
        elif scenario=="Crescita 3%": ral *= 1.03; ral_list.append(ral)
        elif scenario=="Crescita 4%": ral *= 1.04; ral_list.append(ral)
        elif scenario=="Fluttuante bassa": ral *= np.random.uniform(0.995,1.02); ral_list.append(ral)
        elif scenario=="Fluttuante media": ral *= np.random.uniform(0.99,1.03); ral_list.append(ral)
        elif scenario=="Fluttuante alta": ral *= np.random.uniform(0.97,1.05); ral_list.append(ral)
        elif scenario=="Crescita accelerata": ral *= 1.06; ral_list.append(ral)
        elif scenario=="Crescita decrescente": ral *= 0.98; ral_list.append(ral)
    return ral_list

# ==============================
# SIMULAZIONI
# ==============================
def simulate_tfr(ral_list, tasso=0.0833, rivalut=0.03):
    tfr_annuo = [r*tasso for r in ral_list]
    saldo=[]
    acc=0
    for t in tfr_annuo:
        acc = acc*(1+rivalut)+t
        saldo.append(acc)
    return tfr_annuo,saldo

def simulate_cometa(ral_list, contr_pers, contr_azi, rend):
    contr_annuo=[]
    saldo=[]
    acc=0
    for r in ral_list:
        tot = r*(contr_pers+contr_azi)
        contr_annuo.append(tot)
        acc = acc*(1+rend)+tot
        saldo.append(acc)
    return contr_annuo,saldo

def prelievo_legale(saldo, tipo):
    # Percentuali massime legali
    perc = {"Spese sanitarie":0.75,"Prima casa":0.75,"Ulteriori esigenze":0.30}
    tasse = {"Spese sanitarie":0.12,"Prima casa":0.23,"Ulteriori esigenze":0.23}
    netto = [s*perc[tipo]*(1-tasse[tipo]) for s in saldo]
    return netto

# ==============================
# RUN SIMULAZIONE
# ==============================
ral_list = generate_ral(ral_iniziale, anni_lavoro, scenario_ral)
tfr_annuo, saldo_tfr = simulate_tfr(ral_list, tasso=0.0833, rivalut=tasso_rivalut_tfr)
cometa_annuo, saldo_cometa = simulate_cometa(ral_list, contrib_personal, contrib_azienda, tasso_cometa)
tfr_netto = prelievo_legale(saldo_tfr, tipo_prelievo)
cometa_netto = prelievo_legale(saldo_cometa, tipo_prelievo)

# ==============================
# CREAZIONE DATAFRAME
# ==============================
df = pd.DataFrame({
    "Anno": np.arange(1,anni_lavoro+1),
    "Età": np.arange(eta_inizio+1,eta_pensione+1),
    "RAL (€)": ral_list,
    "TFR Lordo (€)": saldo_tfr,
    "Cometa Lordo (€)": saldo_cometa,
    "TFR Netto legale (€)": tfr_netto,
    "Cometa Netto legale (€)": cometa_netto
})

numeric_cols = ["RAL (€)","TFR Lordo (€)","Cometa Lordo (€)","TFR Netto legale (€)","Cometa Netto legale (€)"]
df[numeric_cols] = df[numeric_cols].astype(float)

st.subheader("📊 Tabella anno per anno")
st.dataframe(df.style.format("{:,.2f}"))

# ==============================
# GRAFICI
# ==============================
st.subheader("📈 Lordo vs Netto legale")
df_plot = df.melt(id_vars=["Età"], value_vars=["TFR Lordo (€)","Cometa Lordo (€)","TFR Netto legale (€)","Cometa Netto legale (€)"], 
                  var_name="Tipo", value_name="Valore")

chart = alt.Chart(df_plot).mark_line().encode(
    x=alt.X('Età:Q'),
    y=alt.Y('Valore:Q'),
    color=alt.Color('Tipo:N'),
    tooltip=['Età','Tipo','Valore']
)
st.altair_chart(chart,use_container_width=True)

# ==============================
# METRICHE FINALI
# ==============================
st.subheader("📌 Metriche finali")
st.markdown(f"- **TFR Lordo finale (€)**: {df['TFR Lordo (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **Cometa Lordo finale (€)**: {df['Cometa Lordo (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **TFR Netto legale (€)**: {df['TFR Netto legale (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **Cometa Netto legale (€)**: {df['Cometa Netto legale (€)'].iloc[-1]:,.2f}")
st.markdown(f"- **Totale contributi personali (€)**: {sum(cometa_annuo):,.2f}")
st.markdown(f"- **Rendimento Cometa**: {((df['Cometa Lordo (€)'].iloc[-1]-sum(cometa_annuo))/sum(cometa_annuo)*100):.2f}%")
st.markdown(f"- **Rendimento TFR**: {((df['TFR Lordo (€)'].iloc[-1]-sum(tfr_annuo))/sum(tfr_annuo)*100):.2f}%")