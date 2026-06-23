import streamlit as st
import pandas as pd
import base64
import os
import time
import random
import urllib.parse
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Chifa D' Belinda",
    page_icon="🍜",
    layout="centered"
)

# 2. INICIALIZACIÓN DE ESTADOS
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

if "mostrar_modal" not in st.session_state:
    st.session_state["mostrar_modal"] = False
    st.session_state["modal_plato_info"] = None
    st.session_state["modal_origen"] = "Carta"
    st.session_state["modal_categoria"] = "GENERAL"

if "categoria_activa" not in st.session_state:
    st.session_state["categoria_activa"] = None

if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = "menu_categorias"

if "fondo_seleccionado" not in st.session_state:
    st.session_state["fondo_seleccionado"] = "pag1.jpeg"

# 3. FUNCIONES
@st.cache_data
def cargar_imagen_b64(nombre_imagen):
    routes_posibles = [os.path.join("images", nombre_imagen), os.path.join("app", "static", "images", nombre_imagen), nombre_imagen]
    for r in routes_posibles:
        if os.path.exists(r):
            with open(r, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

def aplicar_fondo_stable():
    img_b64 = cargar_imagen_b64(st.session_state["fondo_seleccionado"])
    if img_b64:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0, 0, 0, 0.60), rgba(0, 0, 0, 0.60)), url('data:image/jpeg;base64,{img_b64}') !important;
            background-size: cover !important; 
            background-repeat: no-repeat !important; 
            background-position: center center !important; 
            background-attachment: fixed !important;
        }}
        </style>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_catalogo_limpio():
    nombre_archivo = "Catalogo_Productos.xlsx"
    if os.path.exists(nombre_archivo): 
        df = pd.read_excel(nombre_archivo)
    else: 
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    return df

aplicar_fondo_stable()
df_carta = cargar_catalogo_limpio()

def click_agregar_plato(plato_info, origen, categoria):
    st.session_state["modal_plato_info"] = plato_info
    st.session_state["modal_origen"] = origen
    st.session_state["modal_categoria"] = categoria
    st.session_state["mostrar_modal"] = True

def regresar_a_categorias():
    st.session_state["categoria_activa"] = None
    st.session_state["vista_actual"] = "menu_categorias"

def ir_a_categoria(nombre_cat):
    st.session_state["categoria_activa"] = nombre_cat
    st.session_state["vista_actual"] = "ver_platos"

def eliminar_del_carrito(uid):
    st.session_state.carrito = [item for item in st.session_state.carrito if item["uid"] != uid]

@st.dialog("Configura tu Plato 🍜")
def abrir_modal_dinamico():
    p_info = st.session_state["modal_plato_info"]
    p_orig = st.session_state["modal_origen"]
    
    st.markdown(f"### {p_info['Name']}")
    cantidad = st.number_input("Cantidad:", min_value=1, max_value=20, value=1, step=1)
    notas = st.text_input("Notas (Opcional):")

    if st.button("🛒 AGREGAR"):
        nuevo_item = {
            "uid": time.time(), "nombre": p_info["Name"], "precio": float(p_info["Price"]),
            "cant": int(cantidad), "tipo": p_orig, "notas": notas
        }
        st.session_state["carrito"].append(nuevo_item)
        st.session_state["mostrar_modal"] = False
        st.rerun()

# 4. CSS MAESTRO
st.markdown("""
<style>
.cabecera-fija-chifa { position: fixed; top: 0; left: 0; right: 0; z-index: 9999; background: rgba(0,0,0,0.85); padding: 15px; text-align: center; border-bottom: 2px solid #FFEB3B; }
div[data-testid="stTabs"] { margin-top: 100px; }
</style>
""", unsafe_allow_html=True)

# 5. LÓGICA DE HORARIO CORREGIDA
hora_actual = datetime.now().time()
hora_inicio = datetime.strptime("11:00", "%H:%M").time()
hora_fin = datetime.strptime("16:30", "%H:%M").time()

# El menú está activo si la hora está entre 11:00 y 16:30
menu_activo = (hora_actual >= hora_inicio and hora_actual <= hora_fin)

# 6. INTERFAZ
st.markdown('<div class="cabecera-fija-chifa"><h2>🍜 CHIFA D\' BELINDA</h2></div>', unsafe_allow_html=True)

tab_menu, tab_carta, tab_pedido = st.tabs(["🍱 Menú del Día", "📖 Carta", "🛒 Pedido"])

with tab_menu:
    if not menu_activo:
        st.warning("⏰ El Menú del Día está disponible de 11:00 AM a 4:30 PM.")
    else:
        st.success("✅ ¡El Menú del Día está disponible ahora!")
        # Aquí iría tu lógica de mostrar platos del menú...

with tab_carta:
    # Lógica de categorías y platos...
    st.write("Contenido de la carta...")

with tab_pedido:
    st.write("Carrito...")

if st.session_state["mostrar_modal"]:
    abrir_modal_dinamico()
