import os
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import Flask, render_template_string, request, redirect, url_for

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("https://cngsfkwkaodbopikrplm.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_ZByXGOuhARBXw_0w_xbN3w_qld1NU2P")

# Inicializar cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Diseño de la página web integrada
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Taller Mecánico - Autopartes</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f4f6f9; color: #333; }
        .container { max-width: 1000px; margin: auto; }
        h1, h2 { color: #1e293b; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        form { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .full-width { grid-column: span 2; }
        input, textarea { padding: 10px; border: 1px solid #cbd5e1; border-radius: 4px; width: 100%; box-sizing: border-box; }
        button { background: #2563eb; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #1d4ed8; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 14px; }
        th { background: #e2e8f0; color: #1e293b; }
        .msg { padding: 12px; margin-bottom: 15px; border-radius: 4px; background: #d1fae5; color: #065f46; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Sistema de Gestión - Taller Mecánico</h1>
        
        {% if mensaje %}
            <div class="msg">{{ mensaje }}</div>
        {% endif %}

        <div class="card">
            <h2>Registrar Nueva Autoparte</h2>
            <form method="POST" action="/agregar">
                <div>
                    <label>Código SKU:</label>
                    <input type="text" name="sku" required>
                </div>
                <div>
                    <label>Nombre de la Pieza:</label>
                    <input type="text" name="nombre" required>
                </div>
                <div>
                    <label>Categoría:</label>
                    <input type="text" name="categoria">
                </div>
                <div>
                    <label>Ubicación en Estante:</label>
                    <input type="text" name="ubicacion">
                </div>
                <div>
                    <label>Precio ($):</label>
                    <input type="number" step="0.01" name="precio" required>
                </div>
                <div>
                    <label>Stock Inicial:</label>
                    <input type="number" name="stock" required>
                </div>
                <div class="full-width">
                    <label>Descripción:</label>
                    <textarea name="descripcion" rows="2"></textarea>
                </div>
                <div class="full-width">
                    <button type="submit">Guardar en Supabase</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>Catálogo Actual de Inventario</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>SKU</th>
                        <th>Nombre</th>
                        <th>Categoría</th>
                        <th>Precio</th>
                        <th>Stock</th>
                        <th>Ubicación</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in catalogo %}
                    <tr>
                        <td>{{ item.id }}</td>
                        <td>{{ item.codigo_sku }}</td>
                        <td>{{ item.nombre }}</td>
                        <td>{{ item.categoria }}</td>
                        <td>${{ item.precio }}</td>
                        <td>{{ item.stock }}</td>
                        <td>{{ item.ubicacion_estante }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    try:
        respuesta = supabase.table("autopartes").select("*").execute()
        catalogo = respuesta.data
    except Exception as e:
        catalogo = []
    mensaje = request.args.get("mensaje")
    return render_template_string(HTML_TEMPLATE, catalogo=catalogo, mensaje=mensaje)

@app.route("/agregar", methods=["POST"])
def agregar():
    sku = request.form.get("sku")
    nombre = request.form.get("nombre")
    categoria = request.form.get("categoria")
    descripcion = request.form.get("descripcion")
    precio = float(request.form.get("precio", 0))
    stock = int(request.form.get("stock", 0))
    ubicacion = request.form.get("ubicacion")

    try:
        datos = {
            "codigo_sku": sku,
            "nombre": nombre,
            "categoria": categoria,
            "descripcion": descripcion,
            "precio": precio,
            "stock": stock,
            "ubicacion_estante": ubicacion
        }
        supabase.table("autopartes").insert(datos).execute()
        mensaje = f"¡Pieza '{nombre}' registrada con éxito!"
    except Exception as e:
        mensaje = f"Error al registrar: {e}"

    return redirect(url_for("index", mensaje=mensaje))

if __name__ == "__main__":
    app.run(debug=True)
