import streamlit as st
import pandas as pd
import numpy as np

# ==============================
# FUNZIONI FINANZIARIE
# ==============================

def mortgage_payment(principal, annual_rate, years):
    """Calcola rata mensile mutuo"""
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)

def annual_mutuo_schedule(principal, rates, years, annual_savings, annual_returns):
    """Calcola anno per anno risparmi, capitale residuo e pagamenti"""
    remaining_capital = []
    saved_total = []
    total_payment = []
    total_savings = 0

    for i in range(years):
        # Risparmi accumulati
        total_savings *= (1 + annual_returns[i])
        total_savings += annual_savings[i]
        saved_total.append(total_savings)

        # Riduzione capitale residuo
        current_principal = max(principal - total_savings, 0)
        remaining_capital.append(current_principal)

        # Pagamento annuo mutuo
        annual_rate = rates[i]
        pay = mortgage_payment(current_principal, annual_rate, 1) * 12
        total_payment.append(pay)

    return saved_total, remaining_capital, total_payment

# ==============================
# STREAMLIT APP
# ==============================

st.title("Simulatore Decisione Mutuo - Anno per Anno")

# ------------------------------
# Input principali
# ------------------------------
st.sidebar.header("Parametri Generali")
principal = st.sidebar.number_input("Importo Mutuo (€)", 10000, 1000000, 250000, step=5000)
duration = st.sidebar.number_input("Durata Mutuo (anni)", 1, 50, 20)
wait_max = st.sidebar.number_input("Anni Attesa Max", 0, 10, 5)
st.sidebar.markdown("### Tipo di variazione tassi e risparmi")
variation_type = st.sidebar.selectbox("Tipo variazione", 
                                      ["Lineare Crescente", "Lineare Decrescente", "Irregolare/Crisi"])

# ------------------------------
# Generazione tassi e risparmi per anno
# ------------------------------
st.sidebar.markdown("### Tassi e Risparmi Anno per Anno")

def generate_values(start, end, years, kind="linear"):
    if kind=="linear":
        return np.linspace(start, end, years).tolist()
    elif kind=="decreasing":
        return np.linspace(end, start, years).tolist()
    else:
        # Irregolare/Crisi: random con trend
        arr = np.linspace(start, end, years)
        noise = np.random.uniform(-0.005, 0.005, years)
        return (arr + noise).tolist()

rates = generate_values(0.02, 0.05, duration, 
                        "linear" if variation_type=="Lineare Crescente" else 
                        "decreasing" if variation_type=="Lineare Decrescente" else "irregular")

savings = generate_values(5000, 15000, duration, 
                        "linear" if variation_type=="Lineare Crescente" else 
                        "decreasing" if variation_type=="Lineare Decrescente" else "irregular")

returns = [0.02]*duration  # rendimento risparmi fisso per semplicità

# Tabella input (bloccata)
df_input = pd.DataFrame({
    "Anno": np.arange(1,duration+1),
    "Tasso (%)": np.array(rates)*100,
    "Risparmio (€)": np.array(savings)
})
st.sidebar.dataframe(df_input)

# ------------------------------
# Calcolo anno per anno
# ------------------------------
saved_total, remaining_capital, total_payment = annual_mutuo_schedule(principal, rates, duration, savings, returns)
interests = [pay - rem for pay, rem in zip(total_payment, remaining_capital)]
gain_vs_subito = [principal*1.02 - pay for pay in total_payment]  # esempio semplice

df_output = pd.DataFrame({
    "Anno": np.arange(1,duration+1),
    "Capitale Residuo (€)": remaining_capital,
    "Interessi (€)": interests,
    "Risparmi Accumulati (€)": saved_total,
    "Pagamento Annuale (€)": total_payment,
    "Guadagno vs Subito (€)": gain_vs_subito
})
st.subheader("Tabella Valori Anno per Anno")
st.dataframe(df_output)

# ------------------------------
# Grafici - due schermate 6+6 metriche
# ------------------------------
import altair as alt

metrics1 = [
    ("Capitale Residuo (€)", remaining_capital, "Capitale residuo dopo risparmi e pagamenti"),
    ("Interessi (€)", interests, "Interessi pagati ogni anno"),
    ("Guadagno vs Subito (€)", gain_vs_subito, "Guadagno netto rispetto pagamento immediato"),
    ("Risparmi Accumulati (€)", saved_total, "Totale risparmi accumulati anno per anno"),
    ("Pagamento Annuale (€)", total_payment, "Totale pagamento annuo mutuo")
]

metrics2 = [
    ("Tassi (%)", np.array(rates)*100, "Tasso applicato ogni anno"),
    ("Risparmi (€)", savings, "Risparmi annuali secondo scenario"),
    ("Rata Mensile (€)", [x/12 for x in total_payment], "Rata mensile del mutuo"),
    ("Costo/Capitale", [pay/principal for pay in total_payment], "Rapporto costo capitale"),
    ("Sensibilità Interessi", np.gradient(interests), "Variazione anno per anno degli interessi")
]

def plot_metrics(metrics, title):
    st.subheader(title)
    for name, values, desc in metrics:
        chart_data = pd.DataFrame({"Anno": np.arange(1,duration+1), name: values})
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x="Anno",
            y=name,
            tooltip=["Anno", name]
        ).properties(
            title=f"{name}: {desc}"
        )
        st.altair_chart(chart, use_container_width=True)

st.subheader("Grafici Schermata 1")
plot_metrics(metrics1, "Metriche principali mutuo")

st.subheader("Grafici Schermata 2")
plot_metrics(metrics2, "Metriche secondarie mutuo")