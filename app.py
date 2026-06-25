import streamlit as st
import pandas as pd
import base64
import os
import time
import random
import urllib.parse
from datetime import datetime, timedelta, timezone  # <-- NUEVO: Manejo de tiempo y zonas horarias

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
    st.session_state["carrito_activa"] = None

if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = "menu_categorias"

if "fondo_seleccionado" not in st.session_state:
    st.session_state["fondo_seleccionado"] = "pag1.jpeg"

# 3. FUNCIONES DE CARGA Y ESTILOS
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
        .main, [data-testid="stCanvas"], [data-testid="stTabPanel"], div[role="tabpanel"], div[data-testid="stVerticalBlock"], [data-testid="stApp"], [data-testid="stHeader"] {{
            background-color: transparent !important; background: transparent !important; box-shadow: none !important;
        }}
        </style>
        """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_catalogo_limpio():
    nombre_archivo = "Catalogo_Productos.xlsx"
    nombre_csv = "Catalogo_Productos.xlsx - in.csv"
    if os.path.exists(nombre_archivo): df = pd.read_excel(nombre_archivo)
    elif os.path.exists(nombre_csv): df = pd.read_csv(nombre_csv)
    else: return pd.DataFrame()

    df.columns = df.columns.str.strip()
    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip().str.upper()
    if 'Description' not in df.columns:
        df['Description'] = ""
    else:
        df['Description'] = df['Description'].fillna("").astype(str).str.strip()
    return df

aplicar_fondo_stable()
df_carta = cargar_catalogo_limpio()

# 4. CALLBACKS DE NAVEGACIÓN
def ir_a_categoria(nombre_cat):
    st.session_state["categoria_activa"] = nombre_cat
    st.session_state["vista_actual"] = "ver_platos"

def regresar_a_categorias():
    st.session_state["categoria_activa"] = None
    st.session_state["vista_actual"] = "menu_categorias"

def click_agregar_plato(plato_info, origen, categoria):
    st.session_state["modal_plato_info"] = plato_info
    st.session_state["modal_origen"] = origen
    st.session_state["modal_categoria"] = categoria
    st.session_state["mostrar_modal"] = True

def eliminar_del_carrito(uid):
    st.session_state.carrito = [item for item in st.session_state.carrito if item["uid"] != uid]

# =========================================================
# MODAL DIALOG
# =========================================================
@st.dialog("Configura tu Plato 🍜")
def abrir_modal_dinamico():
    p_info = st.session_state["modal_plato_info"]
    p_orig = st.session_state["modal_origen"]
    p_cat_name = st.session_state["modal_categoria"]

    st.markdown(f"### {p_info['Name']}")
    st.markdown(f"*Tipo:* {p_orig} | *Precio Unitario:* S/. {p_info['Price']:.2f}")
    st.write("---")

    entrada_sel = ""
    if p_orig == "Menú del Día":
        st.markdown("*Elige tu Entrada (Incluida):*")
        entrada_sel = st.radio("", ["Sopa Wantán 🥣", "Wantán Frito 🥟"], horizontal=True, label_visibility="collapsed")
        st.write("---")

    cantidad = st.number_input("Cantidad:", min_value=1, max_value=20, value=1, step=1)
    st.markdown("*Selecciona tus Cremas / Salsas:*")
    c_aji = st.checkbox("Ají 🌶️")
    c_mayo = st.checkbox("Mayonesa ⚪")
    c_ketchup = st.checkbox("Ketchup 🍅")
    c_tamarindo = st.checkbox("Tamarindo 🍯")

    mostrar_limon = any(k in p_cat_name for k in ["ALITAS", "BROASTER"])
    c_limon = st.checkbox("Limón 🍋") if mostrar_limon else False

    notas = st.text_input("Notas / Observaciones (Opcional):", placeholder="Ej: Sin cebolla...")

    if st.button("🛒 AGREGAR AL PEDIDO", use_container_width=True, key="btn_guardar_modal_real"):
        cremas_list = [c for c, val in [("Ají", c_aji), ("Mayonesa", c_mayo), ("Ketchup", c_ketchup), ("Tamarindo", c_tamarindo)] if val]
        if mostrar_limon and c_limon: cremas_list.append("Limón")

        nuevo_item = {
            "uid": time.time() + random.sample(range(100), 1)[0], "id": p_info["ID"], "nombre": p_info["Name"], "precio": float(p_info["Price"]),
            "cant": int(cantidad), "cremas": ", ".join(cremas_list), "notas": notas.strip(), "tipo": p_orig, "entrada": entrada_sel
        }
        st.session_state["carrito"].append(nuevo_item)
        st.session_state["mostrar_modal"] = False
        st.rerun()

# =========================================================
# CSS MAESTRO INYECTADO
# =========================================================
st.markdown("""
<style>
div[data-testid="stManageAppButton"], [data-testid="stManageAppButton"], .stDeployButton {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
}

html, body, [data-testid="stApp"] { margin: 0 !important; padding: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0px !important; padding-bottom: 140px !important; }
.main .block-container { padding-top: 0px !important; padding-bottom: 140px !important; max-width: 100% !important; }

.cabecera-fija-chifa {
    position: fixed !important; top: 0px !important; left: 0px !important; right: 0px !important;
    z-index: 999999 !important; background-color: rgba(0, 0, 0, 0.85) !important;
    backdrop-filter: blur(8px) !important; -webkit-backdrop-filter: blur(8px) !important; padding: 15px 10px !important; text-align: center;
    border-bottom: 2px solid #FFEB3B;
}

div[data-testid="stTabs"] { margin-top: 95px !important; }
div[data-testid="stTabs"] > div:first-child { background-color: transparent !important; padding: 4px 10px !important; border-bottom: 2px solid #FFEB3B !important; }
div[data-testid="stTabs"] button p { color: #FFFFFF !important; font-size: 15px !important; font-weight: bold !important; text-shadow: 2px 2px 3px #000000 !important; }

.contenedor-seccion-platos { padding: 10px 5px 0px 5px !important; margin-bottom: 40px !important; }

div.contenedor-categoria-limpio div.stButton > button {
    display: block !important;
    background: #F5F5F5 !important;
    border: 2px solid #D9D9D9 !important;
    border-radius: 10px !important;
    padding: 14px 10px !important;
    width: 100% !important;
    height: auto !important;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2) !important;
    margin-bottom: 12px !important;
}

div.contenedor-categoria-limpio div.stButton > button p {
    color: #000000 !important;
    font-size: 16px !important;
    font-weight: 900 !important;
    text-shadow: none !important;
}

div.contenedor-categoria-limpio div.stButton > button:hover, 
div.contenedor-categoria-limpio div.stButton > button:active,
div.contenedor-categoria-limpio div.stButton > button:focus {
    background: #E0E0E0 !important;
    border-color: #BDBDBD !important;
}

div.contenedor-categoria-limpio div.stButton > button:hover p,
div.contenedor-categoria-limpio div.stButton > button:active p,
div.contenedor-categoria-limpio div.stButton > button:focus p {
    color: #000000 !important;
    text-shadow: none !important;
}

div.boton-retroceder-contenedor div.stButton > button {
    background-color: #F5F5F5 !important;
    border: 1px solid #BDBDBD !important;
    padding: 8px 15px !important;
    font-size: 14px !important;
    font-weight: bold !important;
    border-radius: 8px !important;
    width: auto !important;
    margin-bottom: 15px !important;
}

div.boton-retroceder-contenedor div.stButton > button p {
    color: #000000 !important;
    text-shadow: none !important;
    font-weight: bold !important;
}

div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: space-between !important; width: 100% !important; }
div[data-testid="stHorizontalBlock"] > div { min-width: 0 !important; display: flex !important; align-items: center !important; }
.contenedor-fila-perfecta-col { display: flex !important; flex-direction: row !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; }
.columna-izquierda-info { display: flex !important; flex-direction: column !important; justify-content: center !important; min-width: 0 !important; flex: 1 !important; margin-right: 8px !important; }

.texto-nombre-plato { color: #FFFFFF !important; font-size: 17px !important; font-weight: 900 !important; line-height: 1.3 !important; text-shadow: -1.5px -1.5px 0 #000, 1.5px -1.5px 0 #000, -1.5px 1.5px 0 #000, 1.5px 1.5px 0 #000 !important; }
.texto-descripcion-plato { color: #FFFFFF !important; font-size: 13.5px !important; font-style: italic !important; margin-top: 2px; display: block; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important; line-height: 1.2; }
.texto-precio-plato { color: #FFEB3B !important; font-size: 16px !important; font-weight: 900 !important; text-shadow: -1.5px -1.5px 0 #000, 1.5px -1.5px 0 #000, -1.5px 1.5px 0 #000, 1.5px 1.5px 0 #000 !important; white-space: nowrap !important; margin-right: 2px; }

div[data-testid="stHorizontalBlock"] div.stButton > button {
    background-color: #FFEB3B !important; color: #000000 !important; border: 2px solid #8B0000 !important;
    border-radius: 6px !important; width: 32px !important; height: 32px !important; min-width: 32px !important;
    max-width: 32px !important; padding: 0px !important; display: inline-flex !important; align-items: center !important;
    justify-content: center !important; font-weight: 900 !important; font-size: 16px !important; box-shadow: 0px 3px 5px rgba(0,0,0,0.5) !important;
}

.divisor-plato { border-bottom: none !important; margin-top: 15px !important; margin-bottom: 15px !important; clear: both; }

@media (max-width: 767px) {
    [data-testid="stVerticalBlock"] { gap: 0.15rem !important; }
    div[data-testid="stHorizontalBlock"] { padding-top: 5px !important; padding-bottom: 5px !important; }
}

.titulo-categoria-chifa { color: #FFEB3B !important; font-size: 18px !important; font-weight: 900 !important; padding: 10px 8px !important; margin-top: 5px !important; margin-bottom: 10px !important; border-left: 5px solid #FFEB3B !important; background-color: rgba(0, 0, 0, 0.7) !important; border-radius: 0 8px 8px 0; text-shadow: 2px 2px 4px #000000 !important; }
div[data-testid="stDialog"] div.stButton > button, div.boton-vaciar-pedido div.stButton > button { width: 100% !important; height: 45px !important; background-color: #FFEB3B !important; color: #8B0000 !important; font-size: 16px !important; font-weight: bold !important; border-radius: 8px !important; display: block !important; border: none !important; }
div.boton-tacho-contenedor div.stButton > button { background-color: #FFEB3B !important; color: #8B0000 !important; font-size: 14px !important; width: 32px !important; height: 32px !important; border-radius: 6px !important; padding: 0px !important; display: flex !important; }
.fila-carrito-ordenada { padding: 8px 0px !important; border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important; width: 100%; }
.linea-principal-carrito { display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: space-between !important; width: 100% !important; }
.texto-plato-carrito { color: #FFFFFF !important; font-size: 15px !important; font-weight: bold !important; text-shadow: 2px 2px 2px #000000 !important; }
.texto-precio-carrito { color: #FFFFFF !important; font-size: 15px !important; font-weight: bold !important; text-shadow: 2px 2px 2px #000000 !important; }
.texto-detalles-resaltados { color: #FFFFFF !important; font-size: 12px !important; font-weight: 500 !important; display: block; margin-left: 36px; opacity: 0.95; text-shadow: 1px 1px 2px #000000 !important; }
.enlace-wa-directo-siempre { display: block !important; background-color: #25D366 !important; color: white !important; text-align: center !important; font-weight: bold !important; font-size: 16px !important; padding: 14px 20px !important; border-radius: 8px !important; text-decoration: none !important; box-shadow: 0px 5px 10px rgba(0,0,0,0.4) !important; margin: 18px 0px !important; border: 1px solid #ffffff !important; font-size: 18px !important; font-weight: 900 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.4) !important; }
.alerta-delivery-destacada { background-color: rgba(0, 0, 0, 0.75) !important; border: 2px solid #FFEB3B !important; padding: 15px !important; border-radius: 10px !important; color: #FFFFFF !important; margin-bottom: 15px; }
.recuadro-total-final { background-color: rgba(0, 0, 0, 0.5) !important; border: 1px solid #FFEB3B !important; border-radius: 8px !important; padding: 12px 15px !important; margin: 20px 0px !important; display: flex !important; justify-content: space-between !important; }

/* ===== PESTAÑA MI PEDIDO: LABELS E INPUTS ===== */
div[data-testid="stTextInput"] label,
div[data-testid="stRadio"] > label {
    color: #FFEB3B !important;
    font-size: 19px !important;
    font-weight: 900 !important;
    text-shadow: 2px 2px 4px #000000 !important;
}

div[data-testid="stRadio"] label p {
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: bold !important;
    text-shadow: 2px 2px 4px #000000 !important;
}

div[data-testid="stTextInput"] input {
    background-color: #F5F5F5 !important;
    color: #000000 !important;
    font-size: 17px !important;
    font-weight: bold !important;
    border: 2px solid #BDBDBD !important;
    border-radius: 8px !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #444444 !important;
    opacity: 1 !important;
    font-weight: bold !important;
}

div[data-testid="stAlert"] {
    background-color: rgba(255, 0, 0, 0.25) !important;
    border: 1px solid red !important;
}

div[data-testid="stAlert"] p {
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: bold !important;
    text-shadow: 2px 2px 3px #000000 !important;
}

div.boton-vaciar-pedido div.stButton > button {
    background-color: #F5F5F5 !important;
    border: 2px solid #BDBDBD !important;
}

div.boton-vaciar-pedido div.stButton > button p {
    color: #000000 !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    text-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# 5. ENCABEZADO FIJO
st.markdown("""
<div class="cabecera-fija-chifa">
    <h2 style="margin: 0; font-size: 25px; color: #FFEB3B; font-family: sans-serif; text-shadow: 2px 2px 4px #000000;">🍜 CHIFA D' BELINDA</h2>
    <p style="margin: 3px 0 0 0; font-size: 13px; color: #FFFFFF; text-shadow: 1px 1px 2px #000000;">Pedidos en línea rápidos y directos a nuestro WhatsApp</p>
</div>
""", unsafe_allow_html=True)

PLATOS_MENU_INTERNO = [
    {"ID": "M01", "Name": "Chaufa de Pollo", "Price": 14.00},
    {"ID": "M02", "Name": "Alita Rebozada", "Price": 15.00},
    {"ID": "M03", "Name": "1/8 Broaster", "Price": 14.00},
    {"ID": "M04", "Name": "Aeropuerto de Pollo", "Price": 17.00},
    {"ID": "M05", "Name": "Combinado de Pollo", "Price": 17.00},
    {"ID": "M06", "Name": "Pollo con Verdura", "Price": 17.00},
    {"ID": "M07", "Name": "Tallarín Saltado de Pollo", "Price": 17.00},
    {"ID": "M08", "Name": "Pollo con Tamarindo", "Price": 17.00},
    {"ID": "M09", "Name": "Alita con Tamarindo", "Price": 17.00},
    {"ID": "M10", "Name": "Lomo Saltado de Pollo", "Price": 17.00},
    {"ID": "M11", "Name": "Alitas 4 Pzs", "Price": 18.00},
    {"ID": "M12", "Name": "Tortilla de Verdura", "Price": 19.00},
    {"ID": "M13", "Name": "Alitas con Piña", "Price": 18.00},
    {"ID": "M14", "Name": "Pollo con Piña", "Price": 19.00},
    {"ID": "M15", "Name": "Chaufa de Chancho", "Price": 20.00},
    {"ID": "M16", "Name": "Chaufa de Res", "Price": 20.00},
    {"ID": "M17", "Name": "Chaufa de Molleja", "Price": 20.00},
    {"ID": "M18", "Name": "Chicharrón de Pollo", "Price": 20.00},
    {"ID": "M19", "Name": "Chi Jau Kay", "Price": 20.00},
    {"ID": "M20", "Name": "Kam Lu Wantan", "Price": 20.00},
    {"ID": "M21", "Name": "Enrollado de Pollo", "Price": 20.00},
    {"ID": "M22", "Name": "Tipa Kay", "Price": 20.00},
    {"ID": "M23", "Name": "Tallarín de Res", "Price": 20.00},
    {"ID": "M24", "Name": "Combinado de Res", "Price": 20.00},
    {"ID": "M25", "Name": "Chancho con Piña", "Price": 20.00},
    {"ID": "M26", "Name": "Chancho con Tamarindo", "Price": 20.00},
    {"ID": "M27", "Name": "¼ Broaster", "Price": 22.00},
    {"ID": "M28", "Name": "Alitas a la BBQ (3 piezas)", "Price": 18.00},
    {"ID": "M29", "Name": "Alitas Acevichadas (3 piezas)", "Price": 18.00}
]

items_en_carrito = sum(item["cant"] for item in st.session_state.carrito)
tab_menu, tab_carta, tab_pedido = st.tabs(["🍱 Menú del Día", "📖 Platos a la Carta", f"🛒 Mi Pedido ({items_en_carrito})"])

# PESTAÑA: MENÚ DEL DÍA (CON LÓGICA DE HORARIO INTEGRADA)
with tab_menu:
    zona_horaria_peru = timezone(timedelta(hours=-5))
    hora_actual_peru = datetime.now(zona_horaria_peru).time()
    
    hora_inicio = datetime.strptime("11:00:00", "%H:%M:%S").time()
    hora_fin = datetime.strptime("16:30:00", "%H:%M:%S").time()

    st.markdown('<div class="contenedor-seccion-platos">', unsafe_allow_html=True)
    st.markdown('<div class="titulo-categoria-chifa">🍱 Menú chifa del día</div>', unsafe_allow_html=True)

    if hora_inicio <= hora_actual_peru <= hora_fin:
        for plato in PLATOS_MENU_INTERNO:
            col_izq, col_der = st.columns([0.86, 0.14], gap="small")
            with col_izq:
                st.markdown(f"""<div class="contenedor-fila-perfecta-col"><div class="columna-izquierda-info"><span class="texto-nombre-plato">{plato["Name"]}</span></div><span class="texto-precio-plato">S/. {plato["Price"]:.2f}</span></div>""", unsafe_allow_html=True)
            with col_der:
                st.button("＋", key=f"btn_menu_{plato['ID']}", on_click=click_agregar_plato, args=(plato, "Menú del Día", "MENÚ"))
            st.markdown('<div class="divisor-plato"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: rgba(0,0,0,0.7); padding: 30px; border-radius: 12px; border: 2px dashed #FFEB3B; text-align: center; margin-top: 20px;">
            <h3 style="color: #FFEB3B; margin-bottom: 10px;">🕒 Menú No Disponible</h3>
            <p style="color: white; font-size: 16px;">Recuerda que nuestro <b>Menú del Día</b> solo está disponible desde las <b>11:00 AM hasta las 4:30 PM</b>.</p>
            <p style="color: #FFEB3B; font-size: 14px; font-style: italic; margin-top: 15px;">¡Pero no te quedes con hambre! Puedes revisar nuestra variada pestaña de <b>Platos a la Carta</b> que atiende todo el día.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# PESTAÑA: PLATOS A LA CARTA
with tab_carta:
    if df_carta.empty:
        st.warning("⚠️ Por favor, carga tu archivo del catálogo.")
    else:
        if st.session_state["vista_actual"] == "menu_categorias":
            st.markdown('<div class="contenedor-seccion-platos">', unsafe_allow_html=True)
            st.markdown('<p style="color: #FFEB3B; font-weight: bold; margin-bottom: 16px; font-size:16px; text-shadow: 1px 1px 2px black;">📖 Elige una sección de nuestra Carta:</p>', unsafe_allow_html=True)

            categorias_excel = sorted(list(df_carta["Category"].unique()))
            todas_categorias = ["✨ Recomendaciones del Día"] + categorias_excel

            st.markdown('<div class="contenedor-categoria-limpio">', unsafe_allow_html=True)
            for cat in todas_categorias:
                icono = "🔥" if cat == "✨ Recomendaciones del Día" else "🥢"
                st.button(f"{icono} {cat}", key=f"cat_btn_{cat}", on_click=ir_a_categoria, args=(cat,))
            st.markdown('</div></div>', unsafe_allow_html=True)

        elif st.session_state["vista_actual"] == "ver_platos":
            cat_seleccionada = st.session_state["categoria_activa"]

            st.markdown('<div class="boton-retroceder-contenedor">', unsafe_allow_html=True)
            st.button("⬅️ Volver a Categorías", on_click=regresar_a_categorias)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="contenedor-seccion-platos">', unsafe_allow_html=True)
            if cat_seleccionada == "✨ Recomendaciones del Día":
                st.markdown('<div class="titulo-categoria-chifa">🔥 Sugerencias de la casa</div>', unsafe_allow_html=True)
                cats_inicio = ["CHAUFA", "AEROPUERTO", "PLATOS DULCES"]
                df_sugerencias = df_carta[df_carta["Category"].isin(cats_inicio)]

                if not df_sugerencias.empty:
                    if "indices_aleatorios" not in st.session_state:
                        st.session_state["indices_aleatorios"] = random.sample(range(len(df_sugerencias)), min(6, len(df_sugerencias)))
                    valid_indices = [i for i in st.session_state["indices_aleatorios"] if i < len(df_sugerencias)]
                    df_aleatorio = df_sugerencias.iloc[valid_indices] if valid_indices else df_sugerencias.head(6)

                    for idx, row in df_aleatorio.iterrows():
                        plato_dict = {"ID": row["ID"], "Name": row["Name"], "Price": row["Price"]}
                        col_izq, col_der = st.columns([0.86, 0.14], gap="small")
                        with col_izq:
                            st.markdown(f"""<div class="contenedor-fila-perfecta-col"><div class="columna-izquierda-info"><span class="texto-nombre-plato">{row["Name"]} <small style="color:#FFEB3B; font-size:9px;">({row["Category"]})</small></span></div><span class="texto-precio-plato">S/. {float(row["Price"]):.2f}</span></div>""", unsafe_allow_html=True)
                        with col_der:
                            st.button("＋", key=f"btn_sug_{row['ID']}_{idx}", on_click=click_agregar_plato, args=(plato_dict, "Carta", row["Category"]))
                        st.markdown('<div class="divisor-plato"></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="titulo-categoria-chifa">📂 {cat_seleccionada.title()}</div>', unsafe_allow_html=True)
                df_filtrado_cat = df_carta[df_carta["Category"] == cat_seleccionada]
                if not df_filtrado_cat.empty:
                    for idx, row in df_filtrado_cat.iterrows():
                        plato_dict = {"ID": row["ID"], "Name": row["Name"], "Price": row["Price"]}
                        desc_html = ""
                        if cat_seleccionada == "COMBOS" and str(row["Description"]).strip():
                            desc_html = f'<span class="texto-descripcion-plato">✨ {row["Description"]}</span>'

                        col_izq, col_der = st.columns([0.86, 0.14], gap="small")
                        with col_izq:
                            st.markdown(f"""<div class="contenedor-fila-perfecta-col"><div class="columna-izquierda-info"><span class="texto-nombre-plato">{row["Name"]}</span>{desc_html}</div><span class="texto-precio-plato">S/. {float(row["Price"]):.2f}</span></div>""", unsafe_allow_html=True)
                        with col_der:
                            st.button("＋", key=f"btn_carta_{row['ID']}_{idx}", on_click=click_agregar_plato, args=(plato_dict, "Carta", cat_seleccionada))
                        st.markdown('<div class="divisor-plato"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# PESTAÑA: MI PEDIDO
with tab_pedido:
    st.markdown('<div class="contenedor-seccion-platos">', unsafe_allow_html=True)
    if not st.session_state.carrito:
        st.markdown('<h3 style="color: white; text-shadow: 2px 2px 2px black;">Tu carrito está vacío.</h3>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 style="color: #FFEB3B; text-shadow: 2px 2px 3px black; font-size:20px;">📋 Resumen del Pedido</h2>', unsafe_allow_html=True)
        total = 0

        for item in list(st.session_state.carrito):
            subtotal = item["precio"] * item["cant"]
            total += subtotal
            
            # --- MODIFICADO: Estructuración y Renderizado en Carrito ---
            detalles_lista = [f"📌 {item.get('tipo','Carta')}"]
            if item.get("entrada"): detalles_lista.append(f"🍲 {item['entrada']}")
            if item.get('cremas'): detalles_lista.append(f"🧂 {item['cremas']}")
            if item.get('notas'):  detalles_lista.append(f"📝 {item['notas']}")
            detalles_html = " | ".join(detalles_lista)

            st.markdown('<div class="fila-carrito-ordenada">', unsafe_allow_html=True)
            col_tacho, col_info = st.columns([0.12, 0.88])
            with col_tacho:
                st.markdown('<div class="boton-tacho-contenedor">', unsafe_allow_html=True)
                st.button("🗑️", key=f"del_{item['uid']}", on_click=eliminar_del_carrito, args=(item['uid'],))
                st.markdown('</div>', unsafe_allow_html=True)
            with col_info:       
                st.markdown(f"""
                <div class="linea-principal-carrito">
                    <span class="texto-plato-carrito" style="color:#000 !important; text-shadow:none !important;">💥 {item["cant"]} &nbsp; {item["nombre"]}</span>
                    <span class="texto-precio-carrito" style="color:#8B0000 !important; text-shadow:none !important;">S/. {subtotal:.2f}</span>
                </div>
                <span class="texto-detalles-resaltados" style="color:#333333 !important;">{detalles_html}</span>
                """, unsafe_allow_html=True)

        st.markdown(f'<div class="recuadro-total-final"><span style="color:#FFF; font-size:16px; font-weight:bold;">💵 TOTAL:</span><span style="color:#FFEB3B; font-size:18px; font-weight:900;">S/. {total:.2f}</span></div>', unsafe_allow_html=True)

        nombre_cliente = st.text_input("Ingresa tu Nombre Completo:", key="nom_cli")
        metodo_entrega = st.radio("Método de Entrega:", ["Delivery Moto 🏍️", "Recojo en Local 🏪"], horizontal=True, key="met_ent")

        direccion_cliente = ""
        if metodo_entrega == "Delivery Moto 🏍️":
            direccion_cliente = st.text_input("Dirección de Envío:", key="dir_cli")
            st.markdown('<div class="alerta-delivery-destacada">🚨 Por favor! envíanos tu ubicación por WhatsApp después de enviar este mensaje para calcular  el costo del delivery.</div>', unsafe_allow_html=True)

        metodo_pago = st.radio("Método de Pago:", ["Yape 📱", "Efectivo 💵"], horizontal=True, key="met_pag")

        datos_validos = True
        if not nombre_cliente.strip():
            st.error("⚠️ Por favor ingresa tu nombre completo para continuar.")
            datos_validos = False
        elif metodo_entrega == "Delivery Moto 🏍️" and not direccion_cliente.strip():
            st.error("⚠️ Por favor ingresa la dirección de envío.")
            datos_validos = False

        if datos_validos:
            mensaje_wa = f"🍜 CHIFA D' BELINDA\n\n👤 Cliente: {nombre_cliente.strip()}\n♻️ Entrega: {metodo_entrega}\n"
            if metodo_entrega == "Delivery Moto 🏍️": 
                mensaje_wa += f"📍 Dirección: {direccion_cliente.strip()}\n"
            mensaje_wa += f"💳 Pago: {metodo_pago}\n-------------------------\n"

            # --- MODIFICADO: Generación de formato limpio para WhatsApp ---
            for item in st.session_state.carrito:
                tipo_txt = "(MENÚ)" if item.get('tipo') == "Menú del Día" else "(CARTA)"
                mensaje_wa += f"✅ {item['cant']} {item['nombre']} {tipo_txt} - S/. {item['precio'] * item['cant']:.2f}\n"
                if item.get("entrada"): 
                    mensaje_wa += f"   ↳ Entrada: {item['entrada']}\n"
                if item.get('cremas'): 
                    mensaje_wa += f"   ↳ {item['cremas']}\n"  # Sin el prefijo "Cremas:"
                if item.get('notas'):  
                    mensaje_wa += f"   ↳ Obs: {item['notas']}\n"

            mensaje_wa += f"-------------------------\n💰 TOTAL: S/. {total:.2f}"
            link_final = f"https://wa.me/51923860158?text={urllib.parse.quote(mensaje_wa)}"
            st.markdown(f'<a href="{link_final}" target="_blank" class="enlace-wa-directo-siempre">💬 ENVIAR PEDIDO A WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.markdown('<a href="#" onclick="return false;" style="background-color: #cccccc !important; color: #666666 !important; cursor: not-allowed;" class="enlace-wa-directo-siempre">💬 COMPLETE SUS DATOS ARRIBA</a>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="boton-vaciar-pedido">', unsafe_allow_html=True)
        if st.button("🗑️ Vaciar Todo el Carrito", use_container_width=True, key="btn_vaciar_pedido_real"):
            st.session_state.carrito = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["mostrar_modal"]:
    abrir_modal_dinamico()
