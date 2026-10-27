import os
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template_string, request, redirect, url_for

# Cargar variables de entorno (para entorno local con .env)
load_dotenv()

# Leer las variables de entorno de forma segura
SUPABASE_URL = os.getenv("https://cngsfkwkaodbopikrplm.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_ZByXGOuhARBXw_0w_xbN3w_qld1NU2P")

# Validación por si Render o el entorno no las encuentran
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan las credenciales de Supabase en las variables de entorno.")

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
