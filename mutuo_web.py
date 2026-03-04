# mutuo_web_altair.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ==============================
# FUNZIONI FINANZIARIE
# ==============================

def mortgage_payment(principal, annual_rate, years):
    """Calcolo rata mensile mutuo"""
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)

def total_cost(principal, annual_rate, years):
    """Costo totale del mutuo"""
    payment = mortgage_payment(principal, annual_rate, years)
    return payment * years * 12

def savings_accumulated(savings_list, returns_list):
    """Calcolo risparmio cumulato anno per anno"""
    total = 0
    totals = []
    for s, r in zip(savings_list, returns_list):
        total *= (1 + r)
        total += s
        totals.append(total)
    return totals

# ==============================
# STREAMLIT APP
# ==============================

st.set_page_config(layout="wide", page_title="Simulatore Mutuo Web")

st.title("Simulatore Mutuo Avanzato Web")

# ------------------------------
# INPUT PRINCIPALE
# ------------------------------

col_inputs, col_table = st.columns([1,2])

with col_inputs:
    st.subheader("Parametri Generali")
    principal = st.number_input("Importo Mutuo (€)", min_value=1000, value=250000, step=1000)
    years = st.number_input("Durata (anni)", min_value=1, value=5)
    
    st.subheader("Tassi annuali per anno")
    rate_str = st.text_area(
        "Inserisci i tassi anno per anno (%) separati da virgola",
        value="2,2.5,3,3.5,4"
    )
    rates = [float(x)/100 for x in rate_str.split(",")]
    
    st.subheader("Risparmi annuali")
    savings_str = st.text_area(
        "Inserisci risparmi anno per anno (€ separati da virgola)",
        value="10000,10000,10000,10000,10000"
    )
    savings = [float(x) for x in savings_str.split(",")]
    
    st.subheader("Rendimenti risparmi")
    returns_str = st.text_area(
        "Inserisci rendimento annuo dei risparmi (%) separati da virgola",
        value="2,2,2,2,2"
    )
    returns = [float(x)/100 for x in returns_str.split(",")]

# ------------------------------
# TABELLONE DEI VALORI
# ------------------------------

with col_table:
    st.subheader("Tabella Risultati Anno per Anno")
    saved_total = savings_accumulated(savings, returns)
    
    remaining_capital = []
    current = principal
    for amt in saved_total:
        remaining = max(principal - amt, 0)
        remaining_capital.append(remaining)
    
    base_cost = total_cost(principal, sum(rates)/len(rates), years)
    new_cost = [total_cost(c, sum(rates)/len(rates), years) for c in remaining_capital]
    gains = [base_cost - nc for nc in new_cost]
    
    df_table = pd.DataFrame({
        "Anno": list(range(1, len(rates)+1)),
        "Tasso (%)": [r*100 for r in rates],
        "Risparmi (€)": savings,
        "Rendimento (%)": [r*100 for r in returns],
        "Risparmio Totale (€)": saved_total,
        "Capitale Residuo (€)": remaining_capital,
        "Costo Mutuo (€)": new_cost,
        "Guadagno (€)": gains
    })
    st.dataframe(df_table, height=400)

# ------------------------------
# GRAFICI SU DUE SCHERMATE
# ------------------------------

st.subheader("Grafici Dashboard 1")

metrics1 = {
    "Crescita Tassi": rates,
    "Risparmi Accumulati": saved_total,
    "Rendimento Cumulativo": np.cumsum(returns).tolist(),
    "Riduzione Capitale": remaining_capital,
    "Costo Mutuo": new_cost,
    "Guadagno Netto": gains
}

for title, values in metrics1.items():
    df_plot = pd.DataFrame({
        "Anno": list(range(1, len(values)+1)),
        title: values
    })
    chart = alt.Chart(df_plot).mark_line(point=True).encode(
        x="Anno",
        y=title
    ).properties(
        title=f"{title} - Mostra andamento nel tempo"
    )
    st.altair_chart(chart, use_container_width=True)

st.subheader("Grafici Dashboard 2")

metrics2 = {
    "Variazione Tassi": np.gradient(rates).tolist(),
    "Variazione Risparmi": np.gradient(savings).tolist(),
    "Costo/Capitale": [c/principal for c in new_cost],
    "Risparmio Totale Finale": saved_total,
    "Capitale Finale": remaining_capital,
    "Rendimento Cumulativo Finale": np.cumsum(returns).tolist()
}

for title, values in metrics2.items():
    df_plot = pd.DataFrame({
        "Anno": list(range(1, len(values)+1)),
        title: values
    })
    chart = alt.Chart(df_plot).mark_line(point=True).encode(
        x="Anno",
        y=title
    ).properties(
        title=f"{title} - Mostra andamento nel tempo"
    )
    st.altair_chart(chart, use_container_width=True)