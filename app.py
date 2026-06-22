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

def aplicar_fondo_fijo():
    # Forzado únicamente a pag1.jpeg
    img_b64 = cargar_imagen_b64("pag1.jpeg")
    if img_b64:
        st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('data:image/jpeg;base64,{img_b64}') !important;
            background-size: cover !important; 
            background-repeat: no-repeat !important; 
            background-position: center center !important; 
            background-attachment: fixed !important;
        }}
        .main, [data-testid="stCanvas"], [data-testid="stTabPanel"], div[role="tabpanel"], div[data-testid="stVerticalBlock"], [data-testid="stApp"], [data-testid="stHeader"] {{
            background-color: transparent !important; 
            background: transparent !important; 
            box-shadow: none !important;
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

df_carta = cargar_catalogo_limpio()

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
# MODAL DE CONFIGURACIÓN
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
# CSS MAESTRO - ENFOCADO EN OPTIMIZACIÓN MÓVIL
# =========================================================
st.markdown("""
<style>
html, body, [data-testid="stApp"] { margin: 0 !important; padding: 0 !important; }

[data-testid="stMainBlockContainer"] { 
    padding-top: 0px !important; 
    padding-bottom: 120px !important; 
    padding-left: 10px !important;
    padding-right: 10px !important;
} 
.main .block-container { padding-top: 0px !important; max-width: 100% !important; }

[data-testid="stVerticalBlock"] > div {
    gap: 0px !important; margin-top: 0px !important; margin-bottom: 0px !important;
    padding-top: 0px !important; padding-bottom: 0px !important;
}

.cabecera-fija-chifa {
    position: fixed !important; top: 0px !important; left: 0px !important; right: 0px !important;
    z-index: 99999 !important; background-color: rgba(20, 0, 0, 0.95) !important;
    backdrop-filter: blur(5px) !important; padding: 10px !important; text-align: center;
    border-bottom: 2px solid #FFEB3B;
}
.bloque-principal-contenido { margin-top: 85px !important; }

.item-plato-mobile-row {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100% !important;
    padding: 4px 0px !important;
}
.bloque-titulo-desc-movil {
    flex: 1 !important;
    padding-right: 8px !important;
}

.texto-plato-titulo {
    color: #FFFFFF !important; font-size: 14px !important; font-weight: bold !important;
    text-shadow: 2px 2px 2px #000000 !important; display: block; margin: 0 !important; line-height: 1.2 !important;
}
.texto-plato-desc {
    color: #CCCCCC !important; font-size: 11px !important; font-style: italic !important;
    text-shadow: 1px 1px 1px #000000 !important; display: block; margin-top: 1px !important;
}
.texto-plato-precio {
    color: #FFEB3B !important; font-size: 14px !important; font-weight: bold !important;
    text-shadow: 2px 2px 2px #000000 !important; white-space: nowrap !important;
    margin-right: 12px !important; width: 65px !important; text-align: right !important;
}

div.btn-agregar-cuadrado div.stButton > button {
    background-color: #FFEB3B !important; color: #000000 !important;
    font-size: 16px !important; font-weight: bold !important; border-radius: 6px !important;
    width: 32px !important; height: 32px !important; padding: 0px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    border: none !important; box-shadow: 0px 1px 3px rgba(0,0,0,0.5) !important;
}

div.bloque-carrito-fijo-global {
    position: fixed !important; bottom: 0px !important; left: 0px !important; right: 0px !important;
    z-index: 9999999 !important; background-color: rgba(26, 26, 26, 0.98) !important;
    padding: 10px 14px !important; border-top: 2px solid #FFEB3B !important;
    box-shadow: 0px -5px 15px rgba(0,0,0,0.8) !important;
}
div.bloque-carrito-fijo-global div.stButton > button {
    background-color: #FFEB3B !important; color: #000000 !important;
    font-size: 16px !important; font-weight: 900 !important; border-radius: 10px !important;
    height: 48px !important; width: 100% !important; border: none !important;
    text-transform: uppercase;
}

.titulo-categoria-recuadro { 
    color: #FFEB3B !important; font-size: 14px !important; font-weight: bold !important; padding: 6px !important; 
    margin-bottom: 6px !important; border-left: 4px solid #FFEB3B !important; 
    background-color: rgba(0, 0, 0, 0.75) !important; border-radius: 0 4px 4px 0; text-shadow: 2px 2px 2px #000000 !important;
}
div.lista-categorias-vertical div.stButton > button {
    background-color: rgba(0, 0, 0, 0.7) !important; color: #FFEB3B !important;
    border: 1px solid rgba(255, 235, 59, 0.4) !important; padding: 12px !important;
    font-size: 14px !important; font-weight: bold !important; border-radius: 8px !important; margin-bottom: 6px !important;
}
.enlace-wa-directo-siempre { display: block !important; background-color: #25D366 !important; color: white !important; text-align: center !important; font-weight: bold !important; font-size: 15px !important; padding: 12px 15px !important; border-radius: 8px !important; text-decoration: none !important; margin: 15px 0px !important; }
.recuadro-total-final { background-color: rgba(0, 0, 0, 0.6) !important; border: 1px solid #FFEB3B !important; border-radius: 8px !important; padding: 10px !important; display: flex !important; justify-content: space-between !important; }
</style>
""", unsafe_allow_html=True)

aplicar_fondo_fijo()

# 4. ENCABEZADO SUPERIOR
st.markdown("""
<div class="cabecera-fija-chifa">
    <h2 style="margin: 0; font-size: 22px; color: #FFEB3B; font-family: sans-serif; text-shadow: 2px 2px 4px #000000;">🍜 CHIFA D' BELINDA</h2>
    <p style="margin: 1px 0 0 0; font-size: 11px; color: #FFFFFF; text-shadow: 1px 1px 2px #000000;">Pedidos directos a nuestro WhatsApp</p>
</div>
""", unsafe_allow_html=True)

items_en_carrito = sum(item["cant"] for item in st.session_state.carrito)

st.markdown('<div class="bloque-principal-contenido">', unsafe_allow_html=True)

# =========================================================
# VISTA A: REVISIÓN DEL PEDIDO
# =========================================================
if st.session_state["vista_actual"] == "ver_pedido":
    st.markdown('<div style="margin-bottom:10px;">', unsafe_allow_html=True)
    st.button("⬅️ Volver a la Carta", on_click=regresar_a_categorias, key="volver_a_carta_desde_ped")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if not st.session_state.carrito:
        st.markdown('<h3 style="color: white; text-shadow: 2px 2px 2px black;">Tu carrito está vacío.</h3>', unsafe_allow_html=True)
    else:
        st.markdown('<h2 style="color: #FFEB3B; text-shadow: 2px 2px 3px black; font-size:18px;">📋 Resumen del Pedido</h2>', unsafe_allow_html=True)
        total = 0

        for i, item in enumerate(st.session_state.carrito):
            subtotal = item["precio"] * item["cant"]
            total += subtotal
            detalles_lista = [f"📌 {item.get('tipo','Carta')}"]
            if item.get("entrada"): detalles_lista.append(f"🍲 {item['entrada']}")
            if item.get('cremas'): detalles_lista.append(f"🧂 {item['cremas']}")
            if item.get('notes'):  detalles_lista.append(f"📝 {item.get('notas')}")

            col_tacho, col_info, col_subt = st.columns([0.15, 0.55, 0.30])
            with col_tacho:
                if st.button("🗑️", key=f"del_{item['uid']}_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()
            with col_info:
                st.markdown(f'<span style="color:#FFF;font-weight:bold;font-size:14px;">{item["cant"]}x {item["nombre"]}</span>', unsafe_allow_html=True)
                st.markdown(f'<span style="color:#CCC;font-size:11px;display:block;">{" | ".join(detalles_lista)}</span>', unsafe_allow_html=True)
            with col_subt:
                st.markdown(f'<span style="color:#FFEB3B;font-weight:bold;display:block;text-align:right;font-size:14px;">S/. {subtotal:.2f}</span>', unsafe_allow_html=True)

        st.markdown(f'<div class="recuadro-total-final"><span style="color:#FFF; font-weight:bold;">💵 TOTAL:</span><span style="color:#FFEB3B; font-weight:900; font-size:16px;">S/. {total:.2f}</span></div>', unsafe_allow_html=True)
        
        nombre_cliente = st.text_input("Ingresa tu Nombre Completo:", key="nom_cli")
        metodo_entrega = st.radio("Método de Entrega:", ["Delivery Moto 🏍️", "Recojo en Local 🏪"], horizontal=True, key="met_ent")

        direccion_cliente = ""
        if metodo_entrega == "Delivery Moto 🏍️":
            direccion_cliente = st.text_input("Dirección de Envío:", key="dir_cli")
        
        metodo_pago = st.radio("Método de Pago:", ["Yape 📱", "Efectivo 💵"], horizontal=True, key="met_pag")

        mensaje_wa = f"🍜 CHIFA D' BELINDA\n\n👤 Cliente: {nombre_cliente.strip()}\n♻️ Entrega: {metodo_entrega}\n"
        if metodo_entrega == "Delivery Moto 🏍️": 
            mensaje_wa += f"📍 Dirección: {direccion_cliente.strip()}\n"
        mensaje_wa += f"💳 Pago: {metodo_pago}\n-------------------------\n"
        
        for item in st.session_state.carrito:
            tipo_txt = "(MENÚ)" if item.get('tipo') == "Menú del Día" else "(CARTA)"
            mensaje_wa += f"✅ {item['cant']}x {item['nombre']} {tipo_txt} - S/. {item['precio'] * item['cant']:.2f}\n"
            if item.get("entrada"): mensaje_wa += f"   ↳ Entrada: {item['entrada']}\n"
            if item.get('cremas'): mensaje_wa += f"   ↳ Cremas: {item['cremas']}\n"
            if item.get('notas'):  mensaje_wa += f"   ↳ Obs: {item.get('notas')}\n"
                
        mensaje_wa += f"-------------------------\n💰 TOTAL: S/. {total:.2f}"
        link_final = f"https://wa.me/51923860158?text={urllib.parse.quote(mensaje_wa)}"

        if not nombre_cliente.strip() or (metodo_entrega == "Delivery Moto 🏍️" and not direccion_cliente.strip()):
            st.markdown('<a href="#" onclick="alert(\'Por favor completa tu nombre y dirección\'); return false;" class="enlace-wa-directo-siempre">💬 ENVIAR PEDIDO A WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.markdown(f'<a href="{link_final}" target="_blank" class="enlace-wa-directo-siempre">💬 ENVIAR PEDIDO A WHATSAPP</a>', unsafe_allow_html=True)

        if st.button("🗑️ Vaciar Todo el Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()

# =========================================================
# VISTA B: MENU DEL DÍA / CARTA
# =========================================================
else:
    tab_menu, tab_carta = st.tabs(["🍱 Menú del Día", "📖 Platos a la Carta"])

    # PESTAÑA: MENÚ DEL DÍA
    with tab_menu:
        st.markdown('<div class="titulo-categoria-recuadro">🍱 MENÚ CHIFA DEL DÍA</div>', unsafe_allow_html=True)
        for plato in PLATOS_MENU_INTERNO:
            col_txt, col_precio, col_btn = st.columns([0.62, 0.23, 0.15])
            with col_txt:
                st.markdown(f'<span class="texto-plato-titulo">{plato["Name"]}</span>', unsafe_allow_html=True)
            with col_precio:
                st.markdown(f'<span class="texto-plato-precio">S/. {plato["Price"]:.2f}</span>', unsafe_allow_html=True)
            with col_btn:
                st.markdown('<div class="btn-agregar-cuadrado">', unsafe_allow_html=True)
                st.button("＋", key=f"btn_menu_{plato['ID']}", on_click=click_agregar_plato, args=(plato, "Menú del Día", "MENÚ"))
                st.markdown('</div>', unsafe_allow_html=True)

    # PESTAÑA: PLATOS A LA CARTA
    with tab_carta:
        if df_carta.empty:
            st.warning("⚠️ Por favor, carga tu archivo del catálogo.")
        else:
            if st.session_state["vista_actual"] == "menu_categorias":
                st.markdown('<p style="color: #FFEB3B; font-weight: bold; margin-bottom: 10px; font-size:14px; text-shadow: 1px 1px 2px black;">📖 Selecciona una sección de la Carta:</p>', unsafe_allow_html=True)
                categorias_excel = sorted(list(df_carta["Category"].unique()))
                todas_categorias = ["✨ Recomendaciones del Día"] + categorias_excel
                
                st.markdown('<div class="lista-categorias-vertical">', unsafe_allow_html=True)
                for cat in todas_categorias:
                    icono = "🔥" if cat == "✨ Recomendaciones del Día" else "🥢"
                    st.button(f"{icono} {cat}", key=f"p_cat_{cat}", on_click=ir_a_categoria, args=(cat,), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            elif st.session_state["vista_actual"] == "ver_platos":
                cat_seleccionada = st.session_state["categoria_activa"]
                
                st.markdown('<div style="margin-bottom:10px;">', unsafe_allow_html=True)
                st.button("⬅️ Volver a Categorías", on_click=regresar_a_categorias, key="back_to_cats_btn")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if cat_seleccionada == "✨ Recomendaciones del Día":
                    st.markdown('<div class="titulo-categoria-recuadro">🔥 SUGERENCIAS DE LA CASA</div>', unsafe_allow_html=True)
                    cats_inicio = ["CHAUFA", "AEROPUERTO", "PLATOS DULCES"]
                    df_sugerencias = df_carta[df_carta["Category"].isin(cats_inicio)]
                    
                    if not df_sugerencias.empty:
                        if "indices_aleatorios" not in st.session_state:
                            st.session_state["indices_aleatorios"] = random.sample(range(len(df_sugerencias)), min(6, len(df_sugerencias)))
                        
                        valid_indices = [i for i in st.session_state["indices_aleatorios"] if i < len(df_sugerencias)]
                        df_aleatorio = df_sugerencias.iloc[valid_indices] if valid_indices else df_sugerencias.head(6)
                        
                        for idx, row in df_aleatorio.iterrows():
                            plato_dict = {"ID": row["ID"], "Name": row["Name"], "Price": row["Price"]}
                            
                            col_txt, col_precio, col_btn = st.columns([0.62, 0.23, 0.15])
                            with col_txt:
                                st.markdown(f'<span class="texto-plato-titulo">{row["Name"]} <small style="color:#FFEB3B; font-size:9px;">({row["Category"]})</small></span>', unsafe_allow_html=True)
                            with col_precio:
                                st.markdown(f'<span class="texto-plato-precio">S/. {float(row["Price"]):.2f}</span>', unsafe_allow_html=True)
                            with col_btn:
                                st.markdown('<div class="btn-agregar-cuadrado">', unsafe_allow_html=True)
                                st.button("＋", key=f"btn_sug_{row['ID']}_{idx}", on_click=click_agregar_plato, args=(plato_dict, "Carta", row["Category"]))
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                else:
                    st.markdown(f'<div class="titulo-categoria-recuadro">📂 {cat_seleccionada}</div>', unsafe_allow_html=True)
                    df_filtrado_cat = df_carta[df_carta["Category"] == cat_seleccionada]
                    if not df_filtrado_cat.empty:
                        for idx, row in df_filtrado_cat.iterrows():
                            plato_dict = {"ID": row["ID"], "Name": row["Name"], "Price": row["Price"]}
                            
                            col_txt, col_precio, col_btn = st.columns([0.62, 0.23, 0.15])
                            with col_txt:
                                st.markdown(f'<span class="texto-plato-titulo">{row["Name"]}</span>', unsafe_allow_html=True)
                                if str(row["Description"]).strip():
                                    st.markdown(f'<span class="texto-plato-desc">{row["Description"]}</span>', unsafe_allow_html=True)
                            with col_precio:
                                st.markdown(f'<span class="texto-plato-precio">S/. {float(row["Price"]):.2f}</span>', unsafe_allow_html=True)
                            with col_btn:
                                st.markdown('<div class="btn-agregar-cuadrado">', unsafe_allow_html=True)
                                st.button("＋", key=f"btn_carta_{row['ID']}_{idx}", on_click=click_agregar_plato, args=(plato_dict, "Carta", cat_seleccionada))
                                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# BOTÓN DE CARRITO SEGURO ABAJO (FLOTANTE FIJO)
# =========================================================
st.markdown('<div class="bloque-carrito-fijo-global">', unsafe_allow_html=True)
st.button(f"🛒 Ver mi Pedido ({items_en_carrito})", key="btn_fijo_inferior_perfecto", on_click=ir_a_pedido)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state["mostrar_modal"]:
    abrir_modal_dinamico()
