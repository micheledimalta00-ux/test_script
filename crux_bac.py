import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Formula SAE Cruciverba 🎓", layout="wide")
st.title("Simulatore Formula SAE & Cruciverba 🏎️🧩")
st.markdown("Completa le simulazioni, sblocca le parole e scopri la parola finale!")

# --- Definizione mini-giochi e parole soluzione ---
giochi = {
    "Accelerazione": {
        "descrizione": "Raggiungi velocità target evitando slittamento.",
        "parametri": ["m","mu","v0"],
        "indovinello": "Quale parte del veicolo contribuisce alla potenza al suolo durante l’accelerazione?",
        "soluzione": "MOTORE"
    },
    "Slalom": {
        "descrizione": "Percorri il percorso a slalom con rollio minimo.",
        "parametri": ["m","sosp","mu","v0"],
        "indovinello": "Il veicolo a quattro ruote che stai guidando",
        "soluzione": "AUTO"
    },
    "Curva90": {
        "descrizione": "Curva stretta: minimizza rollio e slittamento.",
        "parametri": ["m","sosp","mu","v0","raggio"],
        "indovinello": "Nome della parte che permette di piegare senza cadere",
        "soluzione": "SION"
    },
    "Frenata": {
        "descrizione": "Frenata d’emergenza senza bloccare le ruote.",
        "parametri": ["m","mu","v0"],
        "indovinello": "Sistema che evita il bloccaggio ruote",
        "soluzione": "ABS"
    },
    "Endurance": {
        "descrizione": "Mantieni stabilità e velocità ottimale in percorso combinato.",
        "parametri": ["m","sosp","v0"],
        "indovinello": "Valore che indica quanto l’auto mantiene la traiettoria laterale",
        "soluzione": "LATERALE"
    }
}

# --- Selezione gioco ---
st.sidebar.header("Seleziona la prova")
scelta_gioco = st.sidebar.selectbox("Prova", list(giochi.keys()))
gioco = giochi[scelta_gioco]
st.header(f"Prova: {scelta_gioco}")
st.write(gioco["descrizione"])
st.info(f"Indovinello: {gioco['indovinello']}")

# --- Parametri gioco ---
param = {}
if "m" in gioco["parametri"]:
    param["m"] = st.slider("Massa (kg)", 800, 2000, 1200)
if "sosp" in gioco["parametri"]:
    param["sosp"] = st.slider("Rigidità sospensioni (N/m)", 20000, 50000, 30000)
if "mu" in gioco["parametri"]:
    param["mu"] = st.slider("Attrito gomme", 0.6, 1.2, 0.9)
if "v0" in gioco["parametri"]:
    param["v0"] = st.slider("Velocità iniziale (m/s)", 5, 50, 20)
if "raggio" in gioco["parametri"]:
    param["raggio"] = st.slider("Raggio curva (m)", 5, 50, 15)

# --- Simulazione semplificata ---
t = np.linspace(0, 10, 300)
# inizializzo sempre y e rollio
y = np.zeros_like(t)
rollio = np.zeros_like(t)

if scelta_gioco == "Accelerazione":
    accel = param.get("mu",0.9)*9.81
    v = accel*t
    x = 0.5*accel*t**2
    successo = v[-1]>=30
elif scelta_gioco == "Slalom":
    x = np.sin(t*2)*5
    y = t
    rollio = np.sin(t*2)*2*(50000/param.get("sosp",30000))
    v = np.full_like(t,param.get("v0",20))
    successo = rollio.max()<1.5
elif scelta_gioco == "Curva90":
    r = param.get("raggio",15)
    v0 = param.get("v0",20)
    x = r*np.cos(v0*t/r)
    y = r*np.sin(v0*t/r)
    rollio = np.sin(t*2)*(50000/param.get("sosp",30000))
    v = np.full_like(t,v0)
    successo = rollio.max()<2.0
elif scelta_gioco == "Frenata":
    d_stop = (param.get("v0",20)**2)/(2*param.get("mu",0.9)*9.81)
    x = np.linspace(0,d_stop,len(t))
    y = np.zeros_like(t)
    v = np.linspace(param.get("v0",20),0,len(t))
    rollio = np.zeros_like(t)
    successo = d_stop<=25
elif scelta_gioco == "Endurance":
    x = t
    y = np.sin(t*2)*(50000/param.get("sosp",30000))
    rollio = y
    v = np.full_like(t,param.get("v0",20))
    successo = rollio.max()<1.0

# --- DataFrame con tutte le colonne ---
df = pd.DataFrame({
    "x": x,
    "y": y,
    "Velocità (m/s)": v,
    "Rollio (°)": rollio
})

# --- Grafico Altair ---
chart = alt.Chart(df).mark_line(point=True, color="#1f77b4").encode(
    x='x', y='y',
    tooltip=list(df.columns)
).properties(title="Simulazione")
st.altair_chart(chart, use_container_width=True)

# --- Controllo soglia e memorizzazione parola soluzione ---
if "parole" not in st.session_state:
    st.session_state.parole = {}
st.session_state.parole[scelta_gioco] = gioco["soluzione"] if successo else ""

if successo:
    st.success(f"Complimenti! Hai completato la prova. Parola sbloccata: {gioco['soluzione']}")
else:
    st.warning("Prova non completata. Modifica i parametri e riprova.")

# --- Griglia cruciverba 10x10 ---
st.markdown("### 🧩 Cruciverba")
grid = [["" for _ in range(10)] for _ in range(10)]
# Posizioni parole (esempio semplice)
posizioni = {
    "Accelerazione": (0,0,"H"),
    "Slalom": (2,0,"H"),
    "Curva90": (4,0,"H"),
    "Frenata": (6,0,"H"),
    "Endurance": (8,0,"H")
}

for key, val in posizioni.items():
    parola = st.session_state.parole.get(key,"")
    r,c,orient = val
    for i,l in enumerate(parola):
        if orient=="H" and c+i<10:
            grid[r][c+i] = l
        elif orient=="V" and r+i<10:
            grid[r+i][c] = l

# Visualizzazione griglia
for r in grid:
    st.write(" ".join([l if l!="" else "_" for l in r]))

# --- Controllo parola finale POSTOFISSO ---
finale_rivelata = all([st.session_state.parole.get(k,"") != "" for k in giochi.keys()])
if finale_rivelata:
    st.balloons()
    st.success("🎉 Complimenti! Hai completato tutte le prove. La parola finale è: POSTOFISSO")