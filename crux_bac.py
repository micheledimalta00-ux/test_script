import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Simulatore + Cruciverba 🎓", layout="wide")
st.title("Simulatore di Dinamica Veicolo & Cruciverba 🏎️🧩")
st.markdown("Modifica i parametri dei veicoli, risolvi i problemi e completa il cruciverba per scoprire la parola finale!")

# --- Problemi e parole soluzione ---
problemi = {
    "Slalom": {
        "descrizione": "Completa il percorso a slalom con rollio minimo.",
        "parametri": ["m", "sosp", "mu", "v0"],
        "indizio": "AUTO",
    },
    "Accelerazione": {
        "descrizione": "Raggiungi la velocità target ottimizzando attrito e sospensioni.",
        "parametri": ["m", "mu", "v0"],
        "indizio": "SOSP",
    },
    "Curva90": {
        "descrizione": "Curva a 90°: minimizza rollio e slittamento.",
        "parametri": ["m", "sosp", "mu", "v0", "raggio"],
        "indizio": "SION",
    },
    "Frenata": {
        "descrizione": "Frenata d’emergenza: arresto entro distanza minima senza slittare.",
        "parametri": ["m", "mu", "v0"],
        "indizio": "FOR",
    },
    "Stabilita": {
        "descrizione": "Stabilità post-collisione: minimizza oscillazioni post-impatto.",
        "parametri": ["m", "sosp", "v0"],
        "indizio": "SO",
    }
}

# --- Selezione problema ---
st.sidebar.header("Seleziona problema")
scelta_problema = st.sidebar.selectbox("Problema", list(problemi.keys()))
prob = problemi[scelta_problema]
st.header(f"Problema: {scelta_problema}")
st.write(prob["descrizione"])

# --- Slider parametri ---
parametri = {}
if "m" in prob["parametri"]:
    parametri["m"] = st.slider("Massa (kg)", 800, 2000, 1200)
if "sosp" in prob["parametri"]:
    parametri["sosp"] = st.slider("Rigidità sospensioni (N/m)", 20000, 50000, 30000)
if "mu" in prob["parametri"]:
    parametri["mu"] = st.slider("Attrito gomme", 0.6, 1.2, 0.9)
if "v0" in prob["parametri"]:
    parametri["v0"] = st.slider("Velocità iniziale (m/s)", 5, 50, 20)
if "raggio" in prob["parametri"]:
    parametri["raggio"] = st.slider("Raggio curva (m)", 5, 50, 15)

# --- Simulazioni semplificate ---
t = np.linspace(0, 10, 300)
if scelta_problema == "Slalom":
    x = np.sin(t*2)*5
    y = t
    rollio = np.sin(t*2)*2*(50000/parametri.get("sosp",30000))
    v = np.full_like(t, parametri.get("v0",20))
    soglia_rollio = 1.5
    successo = rollio.max() < soglia_rollio
elif scelta_problema == "Accelerazione":
    x = t * parametri.get("v0",20)
    y = np.zeros_like(t)
    accelerazione = (parametri.get("mu",0.9)*9.81)
    v = accelerazione*t
    successo = v[-1] >= 30
elif scelta_problema == "Curva90":
    r = parametri.get("raggio",15)
    v0 = parametri.get("v0",20)
    x = r * np.cos(v0*t/r)
    y = r * np.sin(v0*t/r)
    rollio = np.sin(t*2)*(50000/parametri.get("sosp",30000))
    v = np.full_like(t, v0)
    successo = rollio.max() < 2.0
elif scelta_problema == "Frenata":
    d_stop = (parametri.get("v0",20)**2)/(2*parametri.get("mu",0.9)*9.81)
    x = np.linspace(0, d_stop, len(t))
    y = np.zeros_like(t)
    v = np.linspace(parametri.get("v0",20),0,len(t))
    successo = d_stop <= 25
elif scelta_problema == "Stabilita":
    x = t
    y = np.sin(t*2)*(50000/parametri.get("sosp",30000))
    rollio = y
    v = np.full_like(t, parametri.get("v0",20))
    successo = rollio.max() < 1.0

df = pd.DataFrame({"x": x, "y": y, "Velocità (m/s)": v})
if "rollio" in locals():
    df["Rollio (°)"] = rollio

# --- Grafico Altair ---
chart = alt.Chart(df).mark_line(point=True, color="#1f77b4").encode(
    x='x', y='y',
    tooltip=list(df.columns)
).properties(title="Simulazione")
st.altair_chart(chart, use_container_width=True)

# --- Controllo soglia e indizio ---
if successo:
    st.success(f"Bravo! Hai completato il problema. Parola sbloccata: {prob['indizio']}")
else:
    st.warning("Parametri non ottimali. Modifica e riprova.")

# --- Memorizzazione parole ottenute ---
if "parole" not in st.session_state:
    st.session_state.parole = {}
st.session_state.parole[scelta_problema] = prob["indizio"] if successo else ""

# --- Visualizzazione cruciverba ---
st.markdown("### 🧩 Cruciverba")
# Griglia: 10x10
grid = [["" for _ in range(10)] for _ in range(10)]
# Posizionamento parole (esempio semplice, verticale/orizzontale)
posizioni = {
    "Slalom": (0,0,"H"), 
    "Accelerazione": (2,0,"H"), 
    "Curva90": (4,0,"H"),
    "Frenata": (6,0,"H"),
    "Stabilita": (8,0,"H")
}
for key, val in posizioni.items():
    parola = st.session_state.parole.get(key,"")
    r, c, orient = val
    for i, lettera in enumerate(parola):
        if orient=="H" and c+i<10:
            grid[r][c+i] = lettera
        elif orient=="V" and r+i<10:
            grid[r+i][c] = lettera

# Stampa griglia
for r in grid:
    st.write(" ".join([l if l!="" else "_" for l in r]))

# --- Controllo parola finale POSTOFISSO ---
# Lettere che compongono POSTOFISSO: posizionate verticalmente su colonne 0 e 1 ad esempio
parola_finale = "POSTOFISSO"
finale_rivelata = all([st.session_state.parole.get(k,"") != "" for k in problemi.keys()])
if finale_rivelata:
    st.balloons()
    st.success(f"🎉 Complimenti! Hai completato tutte le parole. La parola finale è: {parola_finale}")