import streamlit as st
import pandas as pd
import urllib.parse
import base64
import os
import time
import random

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Chifa D' Belinda",
    page_icon="🍜",
    layout="centered"
)

# 2. INICIALIZACIÓN DEL CARRITO Y ESTADOS
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

@st.cache_data
def cargar_imagen_b64(nombre_imagen):
    rutas_posibles = [
        os.path.join("images", nombre_imagen), 
        os.path.join("app", "static", "images", nombre_imagen), 
        nombre_imagen
    ]
    for r in rutas_posibles:
        if os.path.exists(r):
            with open(r, "rb") as f: 
                return base64.b64encode(f.read()).decode()
    return None

def aplicar_fondo_y_estilo_interfaz():
    img_b64 = cargar_imagen_b64("pag1.jpeg")
    if img_b64:
        st.markdown(f"""
        <style>
        /* Fondo completo de la app */
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url('data:image/jpeg;base64,{img_b64}') !important;
            background-size: cover !important; 
            background-repeat: no-repeat !important; 
            background-position: center center !important; 
            background-attachment: fixed !important;
        }}
        
        /* Limpieza de fondos por defecto de Streamlit */
        .main, [data-testid="stCanvas"], [data-testid="stTabPanel"], div[role="tabpanel"], [data-testid="stApp"], [data-testid="stHeader"] {{
            background-color: transparent !important; 
            background: transparent !important; 
            box-shadow: none !important;
        }}

        /* Ajustes de espaciados globales */
        [data-testid="stMainBlockContainer"] {{ 
            padding-top: 15px !important; 
            padding-bottom: 120px !important; 
            padding-left: 10px !important;
            padding-right: 10px !important;
        }}

        /* Reducción de espacios verticales internos */
        [data-testid="stVerticalBlock"] > div {{
            gap: 0px !important; margin-top: 0px !important; margin-bottom: 0px !important;
        }}

        /* --- CONTENEDOR ESTILO DE LA FOTO (RECUADRO CENTRAL OSCURO) --- */
        .contenedor-chifa-interfaz {{
            background-color: rgba(30, 30, 30, 0.82) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 16px !important;
            box-shadow: 0px 8px 32px rgba(0, 0, 0, 0.5) !important;
            margin-bottom: 20px !important;
            width: 100% !important;
        }}

        /* Encabezado elegante centrado */
        .titulo-chifa-encabezado {{
            text-align: center !important;
            margin-bottom: 12px !important;
        }}
        .sublinea-pedidos {{
            font-size: 11px !important;
            color: #FFEB3B !important;
            text-decoration: underline !important;
            font-weight: bold !important;
            letter-spacing: 0.5px;
        }}

        /* Filas de platos y catálogo */
        .item-plato-mobile-row {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            width: 100% !important;
            padding: 6px 0px !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }}

        .texto-plato-titulo {{
            color: #FFFFFF !important; font-size: 14px !important; font-weight: bold !important;
            line-height: 1.2 !important; display: block;
        }}
        .texto-plato-desc {{
            color: #AAAAAA !important; font-size: 11px !important; font-style: italic !important;
            display: block; margin-top: 2px !important;
        }}
        .texto-plato-precio {{
            color: #FFEB3B !important; font-size: 13px !important; font-weight: bold !important;
            white-space: nowrap !important; text-align: right !important; margin-right: 10px !important;
        }}

        /* Botón '+' Amarillo Cuadrado */
        div.btn-agregar-cuadrado div.stButton > button {{
            background-color: #FFEB3B !important; color: #000000 !important;
            font-size: 16px !important; font-weight: bold !important; border-radius: 6px !important;
            width: 32px !important; height: 32px !important; padding: 0px !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            border: none !important;
        }}

        /* Estilo para las Pestañas (Tabs) */
        button[data-baseweb="tab"] {{
            color: #AAAAAA !important; font-size: 13px !important; font-weight: bold !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #FFEB3B !important; border-bottom-color: #FFEB3B !important;
        }}

        /* Botón de categorías vertical */
        div.lista-categorias-vertical div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.5) !important; color: #FFEB3B !important;
            border: 1px solid rgba(255, 235, 59, 0.3) !important; padding: 10px !important;
            font-size: 14px !important; font-weight: bold !important; border-radius: 8px !important; margin-bottom: 6px !important;
        }}

        /* --- BARRA FIJA INFERIOR (CARRITO) --- */
        div.bloque-carrito-fijo-global {{
            position: fixed !important; bottom: 0px !important; left: 0px !important; right: 0px !important;
            z-index: 9999999 !important; background-color: rgba(20, 20, 20, 0.95) !important;
            padding: 12px 14px !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        div.bloque-carrito-fijo-global div.stButton > button {{
            background-color: #FFEB3B !important; color: #000000 !important;
            font-size: 15px !important; font-weight: 900 !important; border-radius: 8px !important;
            height: 46px !important; width: 100% !important; border: none !important;
            text-transform: uppercase; letter-spacing: 0.5px;
        }}

        .enlace-wa-directo-siempre {{ display: block !important; background-color: #25D366 !important; color: white !important; text-align: center !important; font-weight: bold !important; font-size: 15px !important; padding: 12px 15px !important; border-radius: 8px !important; text-decoration: none !important; margin: 15px 0px !important; }}
        .recuadro-total-final {{ background-color: rgba(0, 0, 0, 0.4) !important; border: 1px solid #FFEB3B !important; border-radius: 8px !important; padding: 10px !important; display: flex !important; justify-content: space-between !important; }}
        </style>
        """, unsafe_allow_html=True)

aplicar_fondo_y_estilo_interfaz()

@st.cache_data(ttl=10)
def cargar_catalogo_limpio():
    nombre_archivo = "Catalogo_Productos.xlsx"
    if os.path.exists(nombre_archivo): 
        df = pd.read_excel(nombre_archivo)
    else: 
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.strip().str.upper()
    if 'Description' not in df.columns:
        df['Description'] = ""
    else:
        df['Description'] = df['Description'].fillna("").astype(str).str.strip()
    return df

df_carta = cargar_catalogo_limpio()

# PLATOS DEL MENÚ INTERNO TRADICIONAL
PLATOS_MENU_INTERNO = [
    {"ID": "M1", "Name": "Chaufa de Pollo", "Price": 14.00},
    {"ID": "M2", "Name": "Chaufa de Carne", "Price": 15.00},
    {"ID": "M3", "Name": "Chaufa de Calariuna", "Price": 14.00},
    {"ID": "M4", "Name": "Aeropuerto de Pollo", "Price": 15.00},
    {"ID": "M5", "Name": "Tallarín Saltado de Pollo", "Price": 14.00},
    {"ID": "M6", "Name": "Combinado (Chaufa + Tallarín)", "Price": 15.00}
]

def click_agregar_plato(plato_info, origen, categoria):
    st.session_state["modal_plato_info"] = plato_info
    st.session_state["modal_origen"] = origen
    st.session_state["modal_categoria"] = categoria
    st.session_state["mostrar_modal"] = True

def ir_a_categoria(categoria):
    st.session_state["categoria_activa"] = categoria
    st.session_state["vista_actual"] = "ver_platos"

def regresar_a_categorias():
    st.session_state["vista_actual"] = "menu_categorias"

def ir_a_pedido():
    st.session_state["vista_actual"] = "ver_pedido"

# =========================================================
# MODAL DE CONFIGURACIÓN DIÁLOGO
# =========================================================
@st.dialog("Configura tu Plato 🍜")
def abrir_modal_dinamico():
    p_info = st.session_state["modal_plato_info"]
    p_orig = st.session_state["modal_origen"]
    p_cat_name = st.session_state["modal_categoria"]
    
    st.markdown(f"### {p_info['Name']}")
    st.markdown(f"*Precio:* S/. {p_info['Price']:.2f}")
    st.write("---")
    
    entrada_sel = ""
    if p_orig == "Menú del Día":
        st.markdown("*Elige tu Entrada:*")
        entrada_sel = st.radio("", ["Sopa Wantán 🥣", "Wantán Frito 🥟"], horizontal=True, label_visibility="collapsed")
        st.write("---")

    cantidad = st.number_input("Cantidad:", min_value=1, max_value=20, value=1, step=1)
    st.markdown("*Cremas / Salsas:*")
    c_aji = st.checkbox("Ají Chi Chon San 🌶️")
    c_mayo = st.checkbox("Mayonesa ⚪")
    c_ketchup = st.checkbox("Ketchup 🍅")
    c_tamarindo = st.checkbox("Salsa Tamarindo 🍯")
    
    mostrar_limon = any(k in p_cat_name for k in ["ALITAS", "BROASTER"])
    c_limon = st.checkbox("Limón 🍋") if mostrar_limon else False

    notas = st.text_input("Notas (Opcional):", placeholder="Ej: Sin cebolla...")

    if st.button("🛒 AGREGAR AL PEDIDO", use_container_width=True):
        cremas_list = [c for c, val in [("Ají", c_aji), ("Mayonesa", c_mayo), ("Ketchup", c_ketchup), ("Tamarindo", c_tamarindo)] if val]
        if mostrar_limon and c_limon: cremas_list.append("Limón")
        
        nuevo_item = {
            "uid": time.time() + random.random(), "id": p_info["ID"], "nombre": p_info["Name"], "precio": float(p_info["Price"]),
            "cant": int(cantidad), "cremas": ", ".join(cremas_list), "notas": notas.strip(), "tipo": p_orig, "entrada": entrada_sel
        }
        st.session_state["carrito"].append(nuevo_item)
        st.session_state["mostrar_modal"] = False
        st.rerun()

# =========================================================
# CONTENEDOR VISUAL MAESTRO (INICIO DEL CUADRO OSCURO)
# =========================================================
st.markdown('<div class="contenedor-chifa-interfaz">', unsafe_allow_html=True)

# Encabezado idéntico al de la imagen
st.markdown("""
<div class="titulo-chifa-encabezado">
    <h2 style="margin: 0; font-size: 21px; color: #FFEB3B; font-family: 'Arial', sans-serif;">🍜 CHIFA D' BELINDA</h2>
    <span class="sublinea-pedidos">PEDIDOS DIRECTOS A NUESTRO WHATSAPP</span>
</div>
""", unsafe_allow_html=True)

items_en_carrito = sum(item["cant"] for item in st.session_state.carrito)

# =========================================================
# FILTRADO DE INTERFAZ SEGÚN VISTA
# =========================================================
if st.session_state["vista_actual"] == "ver_pedido":
    st.button("⬅️ Volver a la Carta", on_click=regresar_a_categorias, key="back_to_menu")
    st.write("---")
    
    if not st.session_state.carrito:
        st.markdown('<h4 style="color: white; text-align:center;">Tu carrito está vacío.</h4>', unsafe_allow_html=True)
    else:
        st.markdown('<h3 style="color: #FFEB3B; font-size:16px; margin-bottom:10px;">📋 Tu Pedido:</h3>', unsafe_allow_html=True)
        total = 0
        for i, item in enumerate(st.session_state.carrito):
            subtotal = item["precio"] * item["cant"]
            total += subtotal
            
            col_tacho, col_info, col_subt = st.columns([0.15, 0.55, 0.30])
            with col_tacho:
                if st.button("🗑️", key=f"del_{item['uid']}_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()
            with col_info:
                st.markdown(f'<span style="color:#FFF; font-weight:bold; font-size:13px;">{item["cant"]}x {item["nombre"]}</span>', unsafe_allow_html=True)
                if item.get("entrada") or item.get("cremas"):
                    st.markdown(f'<span style="color:#AAA; font-size:11px;">{item.get("entrada")} {item.get("cremas")}</span>', unsafe_allow_html=True)
            with col_subt:
                st.markdown(f'<span style="color:#FFEB3B; font-weight:bold; text-align:right; display:block; font-size:13px;">S/. {subtotal:.2f}</span>', unsafe_allow_html=True)

        st.markdown(f'<div class="recuadro-total-final"><span style="color:#FFF; font-weight:bold;">💵 TOTAL:</span><span style="color:#FFEB3B; font-weight:bold; font-size:15px;">S/. {total:.2f}</span></div>', unsafe_allow_html=True)
        
        nombre_cliente = st.text_input("Tu Nombre:", key="nom_cli")
        metodo_entrega = st.radio("Entrega:", ["Delivery Moto 🏍️", "Recojo en Local 🏪"], horizontal=True, key="met_ent")
        direccion_cliente = st.text_input("Dirección de Envío:", key="dir_cli") if metodo_entrega == "Delivery Moto 🏍️" else ""
        metodo_pago = st.radio("Pago:", ["Yape 📱", "Efectivo 💵"], horizontal=True, key="met_pag")

        # Armado de mensaje de WhatsApp
        mensaje_wa = f"🍜 CHIFA D' BELINDA\n\n👤 Cliente: {nombre_cliente.strip()}\n♻️ Entrega: {metodo_entrega}\n"
        if direccion_cliente: mensaje_wa += f"📍 Dirección: {direccion_cliente.strip()}\n"
        mensaje_wa += f"💳 Pago: {metodo_pago}\n-------------------------\n"
        for item in st.session_state.carrito:
            mensaje_wa += f"✅ {item['cant']}x {item['nombre']} - S/. {item['precio'] * item['cant']:.2f}\n"
        mensaje_wa += f"-------------------------\n💰 TOTAL: S/. {total:.2f}"
        
        link_final = f"https://wa.me/51923860158?text={urllib.parse.quote(mensaje_wa)}"
        if nombre_cliente.strip():
            st.markdown(f'<a href="{link_final}" target="_blank" class="enlace-wa-directo-siempre">💬 ENVIAR PEDIDO A WHATSAPP</a>', unsafe_allow_html=True)

else:
    tab_menu, tab_carta = st.tabs(["🍱 MENU DEL DÍA", "📖 PLATOS A LA CARTA"])

    with tab_menu:
        for plato in PLATOS_MENU_INTERNO:
            col_txt, col_precio, col_btn = st.columns([0.60, 0.25, 0.15])
            with col_txt:
                st.markdown(f'<span class="texto-plato-titulo">{plato["Name"]}</span>', unsafe_allow_html=True)
            with col_precio:
                st.markdown(f'<span class="texto-plato-precio">S/. {plato["Price"]:.2f}</span>', unsafe_allow_html=True)
            with col_btn:
                st.markdown('<div class="btn-agregar-cuadrado">', unsafe_allow_html=True)
                st.button("＋", key=f"btn_m_{plato['ID']}", on_click=click_agregar_plato, args=(plato, "Menú del Día", "MENÚ"))
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_carta:
        if df_carta.empty:
            st.warning("⚠️ Carga el archivo Catalogo_Productos.xlsx")
        else:
            if st.session_state["vista_actual"] == "menu_categorias":
                categorias_excel = sorted(list(df_carta["Category"].unique()))
                st.markdown('<div class="lista-categorias-vertical">', unsafe_allow_html=True)
                for cat in categorias_excel:
                    st.button(f"🥢 {cat}", key=f"c_{cat}", on_click=ir_a_categoria, args=(cat,), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif st.session_state["vista_actual"] == "ver_platos":
                cat_sel = st.session_state["categoria_activa"]
                st.button("⬅️ Volver a Categorías", on_click=regresar_a_categorias, key="back_to_c")
                st.write("---")
                
                df_filtro = df_carta[df_carta["Category"] == cat_sel]
                for idx, row in df_filtro.iterrows():
                    p_dict = {"ID": row["ID"], "Name": row["Name"], "Price": row["Price"]}
                    
                    col_txt, col_precio, col_btn = st.columns([0.60, 0.25, 0.15])
                    with col_txt:
                        st.markdown(f'<span class="texto-plato-titulo">{row["Name"]}</span>', unsafe_allow_html=True)
                        if str(row["Description"]).strip():
                            st.markdown(f'<span class="texto-plato-desc">{row["Description"]}</span>', unsafe_allow_html=True)
                    with col_precio:
                        st.markdown(f'<span class="texto-plato-precio">S/. {float(row["Price"]):.2f}</span>', unsafe_allow_html=True)
                    with col_btn:
                        st.markdown('<div class="btn-agregar-cuadrado">', unsafe_allow_html=True)
                        st.button("＋", key=f"btn_c_{row['ID']}_{idx}", on_click=click_agregar_plato, args=(p_dict, "Carta", cat_sel))
                        st.markdown('</div>', unsafe_allow_html=True)

# Cierre del div contenedor oscuro
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# BOTÓN DE CARRITO SEGURO ABAJO (FLOTANTE FIJO)
# =========================================================
st.markdown('<div class="bloque-carrito-fijo-global">', unsafe_allow_html=True)
st.button(f"🛒 VER MI PEDIDO ({items_en_carrito})", key="btn_fijo_inferior_perfecto", on_click=ir_a_pedido)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["mostrar_modal"]:
    abrir_modal_dinamico()
