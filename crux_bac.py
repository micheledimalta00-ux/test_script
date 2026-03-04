import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

st.set_page_config(page_title="Arcade SAE Cruciverba", layout="wide")
st.title("Arcade SAE & Cruciverba 🏎️🧩")
st.markdown("Evita gli ostacoli, raccogli parole e completa il cruciverba!")

# --- Impostazioni ---
num_corsie = 3
altezza_strada = 10  # numero di righe visibili
macchina_pos = st.session_state.get("macchina_pos", 1)  # corsia iniziale
tick = st.session_state.get("tick", 0)
livello = st.session_state.get("livello", 1)
parole_racc = st.session_state.get("parole_racc", {})
ostacoli = st.session_state.get("ostacoli", [])
parole_speciali = st.session_state.get("parole_speciali", [])
cruciverba = st.session_state.get("cruciverba", [["_" for _ in range(10)] for _ in range(10)])

# --- Parole per livello ---
parole_livello = {1:"MOTORE",2:"AUTO",3:"SION",4:"ABS",5:"LATERALE"}
num_livelli = len(parole_livello)

# --- Controlli ---
col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("←"):
        macchina_pos = max(0, macchina_pos-1)
with col3:
    if st.button("→"):
        macchina_pos = min(num_corsie-1, macchina_pos+1)

# --- Genera ostacoli e parole speciali per frame ---
if tick % 3 == 0:  # ogni 3 tick nuovo ostacolo/parola
    nuova_riga = ["_" for _ in range(num_corsie)]
    idx_ost = random.randint(0,num_corsie-1)
    nuova_riga[idx_ost] = "X"  # ostacolo
    if random.random()<0.3:  # 30% probabilità parola speciale
        idx_word = random.randint(0,num_corsie-1)
        nuova_riga[idx_word] = "P"
    ostacoli.append(nuova_riga)
    if len(ostacoli)>altezza_strada:
        ostacoli.pop(0)

# --- Collisione e raccolta parole ---
collisione = False
for i,c in enumerate(ostacoli[-1]):
    if i==macchina_pos:
        if c=="X":
            collisione = True
        elif c=="P":
            parole_racc[livello] = parole_livello[livello]
            parole_speciali.append((livello,len(parole_livello[livello])))

# --- Disegna frame con PIL ---
cell_w, cell_h = 60,60
img = Image.new("RGB",(cell_w*num_corsie,cell_h*altezza_strada),(50,50,50))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()

for r,row in enumerate(ostacoli):
    for c,val in enumerate(row):
        x0, y0 = c*cell_w, r*cell_h
        x1, y1 = x0+cell_w, y0+cell_h
        color = (200,0,0) if val=="X" else (0,200,0) if val=="P" else (100,100,100)
        draw.rectangle([x0,y0,x1,y1],fill=color)
        draw.text((x0+cell_w//3, y0+cell_h//3), val,font=font,fill=(255,255,255))

# Macchina
mac_x0, mac_y0 = macchina_pos*cell_w, (altezza_strada-1)*cell_h
draw.rectangle([mac_x0,mac_y0,mac_x0+cell_w,mac_y0+cell_h],fill=(0,0,255))
draw.text((mac_x0+cell_w//3, mac_y0+cell_h//3),"M",font=font,fill=(255,255,255))

st.image(img)

# --- Aggiorna stato sessione ---
st.session_state["macchina_pos"]=macchina_pos
st.session_state["tick"]=tick+1
st.session_state["ostacoli"]=ostacoli
st.session_state["parole_racc"]=parole_racc
st.session_state["parole_speciali"]=parole_speciali
st.session_state["livello"]=livello
st.session_state["cruciverba"]=cruciverba

# --- Collisione ---
if collisione:
    st.error("💥 Collisione! Ripeti il livello.")
    ostacoli.clear()
    st.session_state["tick"]=0

# --- Input cruciverba ---
st.markdown("### 🧩 Cruciverba 10x10")
# Inserisci parole raccolte nella griglia
posizioni = {1:(0,0,"H"),2:(2,0,"H"),3:(4,0,"H"),4:(6,0,"H"),5:(8,0,"H")}
for lvl,pos in posizioni.items():
    parola = parole_racc.get(lvl,"")
    r,c,orient = pos
    for i,l in enumerate(parola):
        if orient=="H" and c+i<10:
            cruciverba[r][c+i] = l
        elif orient=="V" and r+i<10:
            cruciverba[r+i][c] = l

for r in cruciverba:
    st.write(" ".join(r))

# --- Livello successivo ---
if all(lv in parole_racc for lv in range(1,num_livelli+1)):
    st.balloons()
    st.success("🎉 Complimenti! Hai completato tutte le parole. La parola finale è: POSTOFISSO")