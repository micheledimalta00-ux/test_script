import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random

st.set_page_config(page_title="DinoCruciverba", layout="wide")
st.title("DinoCruciverba 🦖🧩")
st.markdown("Salta gli ostacoli, raccogli le parole e completa il cruciverba!")

# --- Parametri gioco ---
larghezza = 20  # colonne del terreno
altezza = 5     # righe, dinosauro in basso
dino_r = altezza-1
dino_c = 2      # colonna fissa
tick = st.session_state.get("tick",0)
salto = st.session_state.get("salto",0)
ostacoli = st.session_state.get("ostacoli",[["_" for _ in range(larghezza)] for _ in range(altezza)])
parole_racc = st.session_state.get("parole_racc",{})
cruciverba = st.session_state.get("cruciverba",[["_"]*10 for _ in range(10)])
livello = st.session_state.get("livello",1)
parole_livello = {1:"MOTORE",2:"AUTO",3:"SION",4:"ABS",5:"LATERALE"}
num_livelli = len(parole_livello)

# --- Controllo salto ---
if st.button("Salta"):
    salto = 2  # dinosauro rimane in aria 2 tick

# --- Aggiorna ostacoli ---
if tick % 2 == 0:  # ogni 2 tick sposta ostacoli verso sinistra
    nuova_colonna = ["_" for _ in range(altezza)]
    # 30% ostacolo
    if random.random()<0.3:
        r = altezza-1
        nuova_colonna[r] = "X"
    # 20% parola speciale
    if random.random()<0.2:
        r = altezza-1
        nuova_colonna[r] = "P"
    # Shift ostacoli
    for r in range(altezza):
        ostacoli[r] = (ostacoli[r][1:] if len(ostacoli[r])>0 else ["_"]) + [nuova_colonna[r]]
        # Normalizza lunghezza
        if len(ostacoli[r]) < larghezza:
            ostacoli[r] = ["_"]*(larghezza - len(ostacoli[r])) + ostacoli[r]
        elif len(ostacoli[r]) > larghezza:
            ostacoli[r] = ostacoli[r][-larghezza:]

# --- Collisione e raccolta parole ---
collisione = False
dino_r_eff = dino_r - salto
for r in range(altezza):
    if ostacoli[r][dino_c] == "X" and r==dino_r_eff:
        collisione = True
    if ostacoli[r][dino_c] == "P" and r==dino_r_eff:
        parole_racc[livello] = parole_livello[livello]

# --- Disegna frame con PIL ---
cell_w, cell_h = 30,30
img = Image.new("RGB",(cell_w*larghezza, cell_h*altezza),(100,100,100))
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
for r in range(altezza):
    for c in range(larghezza):
        val = ostacoli[r][c]
        x0,y0 = c*cell_w, r*cell_h
        x1,y1 = x0+cell_w, y0+cell_h
        color = (200,0,0) if val=="X" else (0,200,0) if val=="P" else (150,150,150)
        draw.rectangle([x0,y0,x1,y1], fill=color)
        draw.text((x0+cell_w//3,y0+cell_h//3),val,font=font,fill=(255,255,255))

# Disegna dinosauro
x0,y0 = dino_c*cell_w, dino_r_eff*cell_h
draw.rectangle([x0,y0,x0+cell_w,y0+cell_h],fill=(0,0,255))
draw.text((x0+cell_w//3,y0+cell_h//3),"D",font=font,fill=(255,255,255))

st.image(img)

# --- Aggiorna stato sessione ---
st.session_state["tick"]=tick+1
st.session_state["salto"]=max(0,salto-1)
st.session_state["ostacoli"]=ostacoli
st.session_state["parole_racc"]=parole_racc
st.session_state["cruciverba"]=cruciverba
st.session_state["livello"]=livello

# --- Collisione ---
if collisione:
    st.error("💥 Collisione! Ripeti il livello")
    ostacoli = [["_" for _ in range(larghezza)] for _ in range(altezza)]
    st.session_state["ostacoli"]=ostacoli
    st.session_state["tick"]=0

# --- Cruciverba 10x10 ---
st.markdown("### 🧩 Cruciverba")
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
    st.success("🎉 Complimenti! Tutte le parole raccolte! POSTOFISSO!")