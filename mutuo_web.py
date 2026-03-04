import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ==============================
# FUNZIONI FINANZIARIE
# ==============================
def mortgage_payment(principal, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


def total_cost(principal, annual_rate, years):
    return mortgage_payment(principal, annual_rate, years) * years * 12


def savings_accumulated(yearly_savings, rate):
    total = 0
    for s in yearly_savings:
        total *= (1 + rate)
        total += s
    return total


# ==============================
# SCENARI
# ==============================
def generate_rates(start, min_r, max_r, years, mode):
    rates = []
    for i in range(years + 1):
        t = i / years if years > 0 else 0
        if mode == "Lineare Crescente":
            val = start + (max_r - start) * t
        elif mode == "Lineare Decrescente":
            val = start - (start - min_r) * t
        elif mode == "Non Lineare Crescente":
            val = start + (max_r - start) * (t ** 2)
        elif mode == "Non Lineare Decrescente":
            val = start - (start - min_r) * (t ** 2)
        elif mode == "Crisi Economica":
            val = start + 0.02 * t if i < years / 2 else max(start - 0.015 * (t - 0.5), min_r)
        else:
            val = start + np.random.normal(0, 0.003)
        val = np.clip(val, min_r, max_r)
        rates.append(val)
    return rates


def generate_savings(start, growth, years, mode, min_s, max_s):
    savings = []
    for i in range(years + 1):
        if mode == "Costante":
            val = start
        elif mode == "Crescente":
            val = start * ((1 + growth) ** i)
        elif mode == "Decrescente":
            val = start * ((1 - growth) ** i)
        elif mode == "Stress Economico":
            val = start if i < years / 2 else start * 0.6
        else:  # Irregolare
            val = start + np.random.normal(0, start * 0.15)
        val = np.clip(val, min_s, max_s)
        savings.append(val)
    return savings


# ==============================
# STREAMLIT APP
# ==============================
st.set_page_config(layout="wide", page_title="Simulatore Mutuo Web")

st.title("Simulatore Mutuo Evoluto (Web)")

# ------------------------------
# INPUT
# ------------------------------
with st.sidebar:
    st.header("Parametri Mutuo")
    P = st.number_input("Importo Mutuo (€)", value=250000)
    years = st.number_input("Durata Mutuo (anni)", value=20)
    wait_max = st.number_input("Anni Attesa Max", value=5)
    
    st.subheader("Tassi")
    rate_start = st.number_input("Tasso Iniziale (%)", value=3.0)/100
    rate_min = st.number_input("Tasso Min (%)", value=2.0)/100
    rate_max = st.number_input("Tasso Max (%)", value=5.0)/100
    rate_mode = st.selectbox("Modalità Variazione Tassi", [
        "Lineare Crescente",
        "Lineare Decrescente",
        "Non Lineare Crescente",
        "Non Lineare Decrescente",
        "Irregolare",
        "Crisi Economica"
    ])
    
    st.subheader("Risparmi Annuali")
    save_start = st.number_input("Risparmio Iniziale (€)", value=10000)
    save_growth = st.number_input("Crescita Risparmio %", value=3.0)/100
    save_min = st.number_input("Risparmio Min (€)", value=5000)
    save_max = st.number_input("Risparmio Max (€)", value=20000)
    save_mode = st.selectbox("Modalità Risparmi", [
        "Costante",
        "Crescente",
        "Decrescente",
        "Irregolare",
        "Stress Economico"
    ])

# ------------------------------
# GENERA SCENARIO
# ------------------------------
rates = generate_rates(rate_start, rate_min, rate_max, wait_max, rate_mode)
savings = generate_savings(save_start, save_growth, wait_max, save_mode, save_min, save_max)

table_data = {"Anno": list(range(wait_max + 1)), "Tasso": rates, "Risparmio": savings}
df_table = pd.DataFrame(table_data)

st.subheader("Scenario Anno per Anno")
st.dataframe(df_table, width=400)

# ------------------------------
# CALCOLO METRICHE
# ------------------------------
waits = np.arange(wait_max + 1)
costs, interests, gains = [], [], []
base_cost = total_cost(P, rates[0], years)
for w in waits:
    saved = savings_accumulated(savings[:w], 0.02)
    new_P = max(P - saved, 0)
    cost = total_cost(new_P, rates[w], years)
    costs.append(cost)
    interests.append(cost - new_P)
    gains.append(base_cost - cost)

descriptions = [
    "Costo totale mutuo rispetto tempo attesa decisionale.",
    "Interessi complessivi pagati lungo durata finanziamento.",
    "Differenza economica rispetto mutuo acceso subito.",
    "Rata media annua stimata in ciascuno scenario.",
    "Capitale effettivamente finanziato dopo risparmi accumulati.",
    "Sensibilità costo totale al ritardo decisione.",
    "Sensibilità interessi al momento ingresso mercato.",
    "Rapporto costo totale su capitale iniziale.",
    "Guadagno medio annuo atteso per anno attesa.",
    "Peso percentuale interessi su costo totale.",
    "Evoluzione tassi secondo scenario scelto.",
    "Evoluzione risparmi annuali nel tempo."
]

metrics = [
    costs,
    interests,
    gains,
    np.array(costs)/years,
    P - np.array(costs),
    np.gradient(costs),
    np.gradient(interests),
    np.array(costs)/P,
    np.array(gains)/(waits+1+1e-6),
    np.array(interests)/np.array(costs),
    rates,
    savings
]

# ------------------------------
# MOSTRA GRAFICI IN 2 SCHEDE
# ------------------------------
tabs = st.tabs(["Metriche 1-6", "Metriche 7-12"])

for idx, tab in enumerate(tabs):
    with tab:
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))
        axs = axs.flatten()
        start = idx * 6
        for i in range(6):
            ax = axs[i]
            y = metrics[start + i]
            desc = descriptions[start + i]
            ax.plot(waits, y, marker='o')
            ax.set_title(desc[:28] + "...")
            ax.set_xlabel("Anni Attesa")
            ax.text(0.5, -0.25, desc, transform=ax.transAxes,
                    ha='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)