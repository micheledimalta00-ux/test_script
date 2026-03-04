import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Arcade SAE Cruciverba 🎓", layout="wide")
st.title("Arcade SAE & Cruciverba 🏎️🧩")
st.markdown("Evita gli ostacoli, completa i livelli e sblocca parole per il cruciverba!")

# --- Impostazioni gioco ---
num_colonne = 5  # corsie
num_livelli = 5
ostacoli_per_livello = 7

# --- Parole soluzione per ogni livello ---
parole_livello = {
    1: "MOTORE",
    2: "AUTO",
    3: "SION",
    4: "ABS",
    5: "LATERALE"
}

# --- Stato sessione ---
if "livello" not in st.session_state:
    st.session_state.livello = 1
if "macchina_pos" not in st.session_state:
    st.session_state.macchina_pos = num_colonne // 2
if "parole_sbloccate" not in st.session_state:
    st.session_state.parole_sbloccate = {}
if "ostacoli" not in st.session_state:
    st.session_state.ostacoli = []

# --- Genera ostacoli per il livello se non esistono ---
if len(st.session_state.ostacoli) < st.session_state.livello:
    ostacoli = []
    for _ in range(ostacoli_per_livello):
        ostacoli.append(np.random.randint(0, num_colonne))
    st.session_state.ostacoli = ostacoli

# --- Controlli giocatore ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("←"):
        st.session_state.macchina_pos = max(0, st.session_state.macchina_pos - 1)
with col2:
    st.write(f"Livello {st.session_state.livello} / {num_livelli}")
with col3:
    if st.button("→"):
        st.session_state.macchina_pos = min(num_colonne - 1, st.session_state.macchina_pos + 1)

# --- Simulazione livello ---
strada = ["_" for _ in range(num_colonne)]
macchina = ["M" if i == st.session_state.macchina_pos else "_" for i in range(num_colonne)]
ostacolo = ["X" if i == st.session_state.ostacoli[st.session_state.livello - 1] else "_" for i in range(num_colonne)]

# --- Controllo collisione ---
collisione = st.session_state.macchina_pos == st.session_state.ostacoli[st.session_state.livello - 1]

if collisione:
    st.error("💥 Collisione! Ripeti il livello.")
else:
    st.success("✅ Nessuna collisione! Parola sbloccata.")
    st.session_state.parole_sbloccate[st.session_state.livello] = parole_livello[st.session_state.livello]

# --- Visualizzazione strada (Altair) ---
df = pd.DataFrame({
    "x": list(range(num_colonne)),
    "y": [1]*num_colonne,
    "tipo": strada
})
# sovrascrivi ostacolo
df.loc[ostacolo.index("X"), "tipo"] = "O"
# sovrascrivi macchina
df.loc[macchina.index("M"), "tipo"] = "M"

chart = alt.Chart(df).mark_text(size=40).encode(
    x='x',
    y='y',
    text='tipo'
).properties(width=400, height=200)
st.altair_chart(chart)

# --- Input cruciverba ---
st.markdown("### 🧩 Cruciverba")
griglia = [["_" for _ in range(10)] for _ in range(10)]
posizioni = {
    1: (0,0,"H"),
    2: (2,0,"H"),
    3: (4,0,"H"),
    4: (6,0,"H"),
    5: (8,0,"H")
}

for lvl, val in posizioni.items():
    parola = st.session_state.parole_sbloccate.get(lvl,"")
    r,c,orient = val
    for i,l in enumerate(parola):
        if orient=="H" and c+i<10:
            griglia[r][c+i] = l
        elif orient=="V" and r+i<10:
            griglia[r+i][c] = l

for r in griglia:
    st.write(" ".join(r))

# --- Bottone passa al livello successivo ---
if st.button("Prossimo livello") and not collisione:
    if st.session_state.livello < num_livelli:
        st.session_state.livello += 1
    st.session_state.macchina_pos = num_colonne // 2

# --- Controllo parola finale POSTOFISSO ---
if len(st.session_state.parole_sbloccate) == num_livelli:
    st.balloons()
    st.success("🎉 Complimenti! Hai completato tutte le parole. La parola finale è: POSTOFISSO")