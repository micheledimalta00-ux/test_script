import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Simulatore + Cruciverba 🎓", layout="wide")
st.title("Simulatore di Dinamica Veicolo & Cruciverba 🏎️🧩")
st.markdown("Modifica i parametri e completa il cruciverba per scoprire la parola finale! 💡")

# --- Parametri del veicolo ---
st.sidebar.header("Parametri del veicolo")
m = st.sidebar.slider("Massa del veicolo (kg)", 800, 2000, 1200)
L = st.sidebar.slider("Lunghezza passo (m)", 2.0, 3.0, 2.5)
b = st.sidebar.slider("Larghezza carreggiata (m)", 1.4, 2.0, 1.6)
mu = st.sidebar.slider("Coefficiente attrito gomme", 0.6, 1.2, 0.9)
v0 = st.sidebar.slider("Velocità iniziale (m/s)", 5, 50, 20)
raggio = st.sidebar.slider("Raggio curva (m)", 5, 50, 10)

# --- Simulazione semplificata ---
t = np.linspace(0, 10, 300)
x = raggio * np.cos(v0 * t / raggio)
y = raggio * np.sin(v0 * t / raggio)
v = np.full_like(t, v0)
F_lat = m * v**2 / raggio

df = pd.DataFrame({
    "Tempo (s)": t,
    "X (m)": x,
    "Y (m)": y,
    "Velocità (m/s)": v,
    "Forza laterale (N)": F_lat
})

# --- Grafici con Altair ---
chart_traiettoria = alt.Chart(df).mark_line(point=True, color="#1f77b4").encode(
    x='X (m)',
    y='Y (m)',
    tooltip=['Tempo (s)', 'Velocità (m/s)', 'Forza laterale (N)']
).interactive().properties(title="Traiettoria del veicolo")

chart_velocità = alt.Chart(df).mark_line(color="#2ca02c").encode(
    x='Tempo (s)',
    y='Velocità (m/s)',
    tooltip=['Tempo (s)', 'Velocità (m/s)']
).properties(title="Velocità vs Tempo")

chart_forza = alt.Chart(df).mark_line(color="#d62728").encode(
    x='Tempo (s)',
    y='Forza laterale (N)',
    tooltip=['Tempo (s)', 'Forza laterale (N)']
).properties(title="Forza Laterale vs Tempo")

col1, col2 = st.columns(2)
col1.altair_chart(chart_traiettoria, use_container_width=True)
col2.altair_chart(chart_velocità + chart_forza, use_container_width=True)

st.markdown("### 🔧 Obiettivo: ottimizza i parametri del veicolo per raggiungere le soglie richieste e ottenere gli indizi per il cruciverba.")

# --- Soglie per ottenere indizi ---
# Definiamo 3 mini-obiettivi
soglie = {
    "A": {"F_lat_max": 15000, "v_max": 25, "indizio": "P"},
    "B": {"F_lat_max": 10000, "v_max": 30, "indizio": "O"},
    "C": {"F_lat_max": 12000, "v_max": 28, "indizio": "S"},
    "D": {"F_lat_max": 13000, "v_max": 22, "indizio": "T"},
    "E": {"F_lat_max": 9000, "v_max": 35, "indizio": "O"},
    "F": {"F_lat_max": 11000, "v_max": 27, "indizio": "F"},
    "G": {"F_lat_max": 10000, "v_max": 26, "indizio": "I"},
    "H": {"F_lat_max": 9500, "v_max": 29, "indizio": "S"},
    "I": {"F_lat_max": 12000, "v_max": 24, "indizio": "S"},
    "J": {"F_lat_max": 12500, "v_max": 28, "indizio": "O"},
}

# --- Controllo dei risultati ---
ottenuti = []
for key, val in soglie.items():
    if F_lat.max() <= val["F_lat_max"] and v0 <= val["v_max"]:
        ottenuti.append(val["indizio"])

if ottenuti:
    st.success(f"Hai ottenuto {len(ottenuti)} indizi: {' '.join(ottenuti)}")
    st.info("Prova a usarli per completare il cruciverba qui sotto!")
else:
    st.warning("Nessun indizio ottenuto. Modifica i parametri e riprova!")

# --- Cruciverba interattivo ---
st.markdown("### 🧩 Cruciverba: scopri la parola finale")
st.markdown("""
Scrivi le lettere ottenute nei riquadri corretti. La parola finale è **POSTOFISSO**.
""")

parola_corrente = st.text_input("Parola finale", "")

if parola_corrente.upper() == "POSTOFISSO":
    st.balloons()
    st.success("🎉 Complimenti! Hai completato il cruciverba e scoperto la parola finale: POSTOFISSO!")
else:
    st.info("Continua a raccogliere indizi dalle simulazioni per completare la parola.")