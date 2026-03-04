import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

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
# APP STREAMLIT
# ==============================
st.set_page_config(page_title="Simulatore Mutuo Evoluto", layout="wide")
st.title("Simulatore Mutuo Evoluto")

# ------------------------------
# INPUT PARAMETRI
# ------------------------------
col1, col2 = st.columns(2)

with col1:
    P = st.number_input("Importo Mutuo (€)", value=250000)
    years = st.number_input("Durata Mutuo (anni)", value=20, min_value=1)
    wait_max = st.number_input("Anni Attesa Max", value=5, min_value=0)
    
    rate_start = st.number_input("Tasso Iniziale", value=0.03, format="%.4f")
    rate_min = st.number_input("Tasso Min", value=0.02, format="%.4f")
    rate_max = st.number_input("Tasso Max", value=0.05, format="%.4f")
    rate_mode = st.selectbox("Scenario Tassi", [
        "Lineare Crescente",
        "Lineare Decrescente",
        "Non Lineare Crescente",
        "Non Lineare Decrescente",
        "Irregolare",
        "Crisi Economica"
    ])

    save_start = st.number_input("Risparmio Iniziale", value=10000)
    save_growth = st.number_input("Crescita Risparmio %", value=0.03)
    save_min = st.number_input("Risparmio Min", value=5000)
    save_max = st.number_input("Risparmio Max", value=20000)
    save_mode = st.selectbox("Scenario Risparmi", [
        "Costante",
        "Crescente",
        "Decrescente",
        "Irregolare",
        "Stress Economico"
    ])

# ------------------------------
# GENERAZIONE TABELLA
# ------------------------------
rates = generate_rates(rate_start, rate_min, rate_max, wait_max, rate_mode)
savings = generate_savings(save_start, save_growth, wait_max, save_mode, save_min, save_max)

table = pd.DataFrame({
    "Anno": np.arange(wait_max + 1),
    "Tasso": rates,
    "Risparmio": savings
})

with col2:
    st.write("### Tassi e Risparmi per Anno")
    st.dataframe(table, use_container_width=True)

# ------------------------------
# CALCOLO METRICHE
# ------------------------------
waits = table["Anno"].values
costs, interests, gains = [], [], []
base_cost = total_cost(P, rates[0], years)

for w in waits:
    saved = savings_accumulated(savings[:w], 0.02)
    new_P = max(P - saved, 0)
    cost = total_cost(new_P, rates[w], years)
    costs.append(cost)
    interests.append(cost - new_P)
    gains.append(base_cost - cost)

metrics = pd.DataFrame({
    "Anni Attesa": waits,
    "Costo Totale": costs,
    "Interessi Totali": interests,
    "Guadagno vs Subito": gains,
    "Capitale Residuo": [P - s for s in np.cumsum(savings)],
    "Rata Mensile": [mortgage_payment(max(P - s, 0), r, years) for s, r in zip(np.cumsum(savings), rates)],
    "Sensibilità Costo": np.gradient(costs),
    "Sensibilità Interessi": np.gradient(interests),
    "Costo/Capitale": np.array(costs)/P,
    "Guadagno Medio Annuo": np.array(gains)/(waits+1e-6)
})

# ------------------------------
# GRAFICI CON ALTair
# ------------------------------
st.write("## Metriche Mutuo")

for col_name in metrics.columns[1:]:
    st.write(f"### {col_name}")
    chart = alt.Chart(metrics).mark_line().encode(
        x="Anni Attesa",
        y=col_name
    ).interactive()
    st.altair_chart(chart, use_container_width=True)