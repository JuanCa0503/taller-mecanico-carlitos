import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Cargar variables de entorno desde el archivo .env
load_dotenv()
# CORRECTO: Leer el nombre de la variable de entorno
SUPABASE_URL = os.getenv("https://cngsfkwkaodbopikrplm.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_ZByXGOuhARBXw_0w_xbN3w_qld1NU2P")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuración de la página web
st.set_page_config(page_title="Taller Mecánico y Autopartes", layout="wide")

st.title("🚗 Sistema de Gestión - Taller Mecánico y Autopartes")
st.markdown("Administra tu inventario y catálogo de piezas directamente desde la web.")

# Menú lateral para navegar entre secciones
menu = st.sidebar.selectbox("Navegación", ["Registrar Autoparte", "Ver Catálogo"])

if menu == "Registrar Autoparte":
    st.subheader("📝 Registrar Nueva Autoparte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sku = st.text_input("Código SKU")
        nombre = st.text_input("Nombre de la Pieza")
        categoria = st.text_input("Categoría")
        descripcion = st.text_area("Descripción")
        
    with col2:
        precio = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
        stock = st.number_input("Stock Inicial", min_value=0, step=1)
        ubicacion = st.text_input("Ubicación en Estante")
    
    if st.button("Guardar en Supabase", type="primary"):
        if sku and nombre:
            try:
                datos = {
                    "codigo_sku": sku,
                    "nombre": nombre,
                    "categoria": categoria,
                    "descripcion": descripcion,
                    "precio": float(precio),
                    "stock": int(stock),
                    "ubicacion_estante": ubicacion
                }
                supabase.table("autopartes").insert(datos).execute()
                st.success(f"¡Pieza '{nombre}' registrada con éxito en la base de datos!")
            except Exception as e:
                st.error(f"Error al registrar la autoparte: {e}")
        else:
            st.warning("Por favor, completa al menos el Código SKU y el Nombre de la pieza.")

elif menu == "Ver Catálogo":
    st.subheader("📦 Catálogo Actual de Autopartes")
    
    if st.button("🔄 Actualizar Tabla"):
        st.rerun()
        
    try:
        respuesta = supabase.table("autopartes").select("*").execute()
        catalogo = respuesta.data
        
        if catalogo:
            # Muestra los datos en una tabla interactiva muy estilizada
            st.dataframe(catalogo, use_container_width=True)
        else:
            st.info("No hay autopartes registradas en este momento.")
    except Exception as e:
        st.error(f"Error al consultar el catálogo: {e}")
