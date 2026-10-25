import libsql
import gradio as gr
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

url_turso = "libsql://tallermecanico-car-rex05.aws-us-west-2.turso.io"
auth_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODk5NTI2MTcsImlkIjoiMDFhMDU4NzEtM2YwMS03ODFkLWIwNzgtM2QxMTRhOGJlYTJlIiwia2lkIjoiLXl6VE9OdUtMY0QtSkxmSFVHUkJ1RjQ5SEtmMFJtbEZVMHRkWnB5SUgzOCIsInJpZCI6IjJiMWU3Mjc2LTRmZWQtNGZhOS1hZWI0LWI0YmZiMzBhMDc1NiJ9._3Bh47awuLjcVsdJLqUVMsdngY9YgCi111jWCSfY3LcDDb3etPvxx8pXTHRmg_dudgZRDgvQlTYU2Jd-c8_TDQ"

conn = libsql.connect(
    database=url_turso,
    auth_token=auth_token
)

print("Conexión realizada correctamente")

# Crear tabla de taller (clientes y reparaciones)
conn.execute("""
CREATE TABLE IF NOT EXISTS taller (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    vehiculos TEXT,
    reparaciones TEXT
)
""")

# Tabla de productos (con columna para imagen de referencia)
conn.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY,
    nombre TEXT,
    descripcion TEXT,
    precio REAL,
    stock INTEGER,
    imagen TEXT
)
""")

conn.commit()


# --- FUNCIONES DE CLIENTES Y REPARACIONES ---

def agregar_cliente(id_cliente, nombre, vehiculo, reparacion):
    try:
        conn.execute("""
        INSERT INTO taller (id, nombre, vehiculos, reparaciones)
        VALUES (?, ?, ?, ?)
        """, (id_cliente, nombre, vehiculo, reparacion))
        conn.commit()
        return "Cliente registrado correctamente."
    except Exception as e:
        return f"Error: {e}"

def mostrar_registros():
    resultado = conn.execute("""
    SELECT * FROM taller
    """)
    datos = resultado.fetchall()
    return datos

def eliminar_cliente(id_cliente):
    try:
        conn.execute(
            "DELETE FROM taller WHERE id = ?",
            (id_cliente,)
        )
        conn.commit()
        return "Registro eliminado correctamente."
    except Exception as e:
        return f"Error: {e}"


# --- FUNCIONES DE PRODUCTOS ---

def agregar_producto(id_prod, nombre, descripcion, precio, stock, imagen):
    try:
        conn.execute("""
        INSERT INTO productos (id, nombre, descripcion, precio, stock, imagen)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (id_prod, nombre, descripcion, precio, stock, imagen))
        conn.commit()
        return "Producto registrado correctamente en el catálogo."
    except Exception as e:
        return f"Error: {e}"

def mostrar_productos():
    resultado = conn.execute("""
    SELECT * FROM productos
    """)
    datos = resultado.fetchall()
    return datos


# --- FUNCIÓN PARA GENERAR PDF DE TURNOS ---

def generar_pdf_turno():
    pdf_path = "reporte_taller.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Taller Mecanico Carlitos - Reporte de Turno")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "Listado general de servicios, clientes e inventario actual.")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, "1. Registro de Clientes y Reparaciones:")
    
    y = height - 120
    resultado_clientes = conn.execute("SELECT * FROM taller").fetchall()
    
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "ID | Nombre | Vehiculo | Reparacion")
    y -= 15

    for row in resultado_clientes:
        if y < 50:
            c.showPage()
            y = height - 50
        texto = f"{row[0]} | {row[1]} | {row[2]} | {row[3]}"
        c.drawString(50, y, texto)
        y -= 15

    y -= 20
    if y < 100:
        c.showPage()
        y = height - 50

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "2. Catalogo de Productos y Refacciones:")
    y -= 20

    resultado_productos = conn.execute("SELECT * FROM productos").fetchall()
    c.setFont("Helvetica", 9)
    c.drawString(50, y, "ID | Nombre | Descripcion | Precio | Stock")
    y -= 15

    for row in resultado_productos:
        if y < 50:
            c.showPage()
            y = height - 50
        texto = f"{row[0]} | {row[1]} | {row[2]} | ${row[3]} | Stock: {row[4]}"
        c.drawString(50, y, texto)
        y -= 15

    c.save()
    return pdf_path


# --- ESTILOS CSS CON DEGRADADO VIOLETA/MORA Y TARJETAS LIMPIAS ---
custom_css = """
body, html, .gradio-container {
    background: linear-gradient(135deg, #3b1464 0%, #6b21a8 50%, #db2777 100%) !important;
    color: #ffffff !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.gr-box, .gr-panel, .gr-group {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
}
h1, h2, h3, p, span, label {
    color: #ffffff !important;
}
"""

# --- INTERFAZ DE GRADIO ---

with gr.Blocks(title="Taller Mecanico Carlitos", css=custom_css) as app:

    # ==================== VISTA 1: PORTADA PRINCIPAL ====================
    with gr.Column(visible=True) as pantalla_portada:
        
        # Cabecera con el título a la izquierda y el botón de administrador arriba a la derecha
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown(
                    """
                    # Taller Mecanico Carlitos
                    ### Sistema integral de control automotriz, servicios e inventario.
                    """
                )
            with gr.Column(scale=1, min_width=220):
                gr.Markdown("")
                btn_ir_admin = gr.Button("Panel de Administrador", variant="primary")

        gr.Markdown("---")

        # Tarjeta central limpia con la identidad y el mensaje institucional
        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                gr.Image(
                    label="Identidad del Taller",
                    interactive=False,
                    height=280
                )
                gr.Markdown(
                    """
                    <h3 style="text-align: center; margin-top: 15px; font-weight: 600;">Calidad y Confianza en el Servicio Automotriz</h3>
                    """
                )


    # ==================== VISTA 2: PANEL DE ADMINISTRACIÓN ====================
    with gr.Column(visible=False) as pantalla_admin:
        
        with gr.Row():
            btn_volver_portada = gr.Button("Volver a la Portada", variant="secondary", scale=0)
            gr.Markdown("## Panel de Administracion - Taller Mecanico Carlitos")

        gr.Markdown("---")

        # Pestañas de gestión dentro del panel de administración
        with gr.Tabs():
            
            # 1. Registrar Cliente
            with gr.Tab("Registrar Cliente"):
                gr.Markdown("### Registro de Nuevo Servicio")
                with gr.Row():
                    id_cliente = gr.Number(label="ID del cliente", precision=0)
                    nombre = gr.Textbox(label="Nombre del cliente", placeholder="Ejemplo: Juan Perez")
                
                with gr.Row():
                    vehiculo = gr.Textbox(label="Vehiculo", placeholder="Ejemplo: Nissan Versa 2020")
                    reparacion = gr.Textbox(label="Reparacion", placeholder="Ejemplo: Cambio de aceite")
                
                boton_guardar = gr.Button("Guardar Registro", variant="primary")
                mensaje = gr.Textbox(label="Estado de la operacion", interactive=False)

                boton_guardar.click(
                    agregar_cliente,
                    inputs=[id_cliente, nombre, vehiculo, reparacion],
                    outputs=mensaje
                )

            # 2. Ver Registros
            with gr.Tab("Ver Registros"):
                gr.Markdown("### Listado de Clientes y Reparaciones")
                tabla = gr.Dataframe(
                    headers=["ID", "Nombre", "Vehiculo", "Reparacion"],
                    label="Registros actuales",
                    interactive=False
                )
                boton_mostrar = gr.Button("Actualizar Registros", variant="secondary")

                boton_mostrar.click(
                    mostrar_registros,
                    outputs=tabla
                )

            # 3. Eliminar Registro
            with gr.Tab("Eliminar Registro"):
                gr.Markdown("### Baja de Registros")
                id_eliminar = gr.Number(label="ID del registro a eliminar", precision=0)
                boton_eliminar = gr.Button("Eliminar Registro", variant="stop")
                mensaje_eliminar = gr.Textbox(label="Estado de la operacion", interactive=False)

                boton_eliminar.click(
                    eliminar_cliente,
                    inputs=id_eliminar,
                    outputs=mensaje_eliminar
                )

            # 4. Catálogo de Productos
            with gr.Tab("Catalogo de Productos"):
                gr.Markdown("### Gestion de Inventario y Refacciones")
                with gr.Row():
                    with gr.Column():
                        id_prod = gr.Number(label="ID del producto", precision=0)
                        nombre_prod = gr.Textbox(label="Nombre", placeholder="Ejemplo: Aceite 5W-30")
                        desc_prod = gr.Textbox(label="Descripcion", placeholder="Bidon de 4 litros")
                        precio_prod = gr.Number(label="Precio ($)")
                        stock_prod = gr.Number(label="Stock", precision=0)
                        imagen_prod = gr.Textbox(label="URL de imagen", placeholder="https://...")
                        
                        boton_guardar_prod = gr.Button("Guardar Producto", variant="primary")
                        mensaje_prod = gr.Textbox(label="Estado", interactive=False)

                        boton_guardar_prod.click(
                            agregar_producto,
                            inputs=[id_prod, nombre_prod, desc_prod, precio_prod, stock_prod, imagen_prod],
                            outputs=mensaje_prod
                        )

                    with gr.Column():
                        tabla_prod = gr.Dataframe(
                            headers=["ID", "Nombre", "Descripcion", "Precio ($)", "Stock", "Imagen URL"],
                            label="Inventario actual",
                            interactive=False
                        )
                        boton_mostrar_prod = gr.Button("Actualizar Catalogo", variant="secondary")

                        boton_mostrar_prod.click(
                            mostrar_productos,
                            outputs=tabla_prod
                        )

            # 5. Reporte PDF
            with gr.Tab("Reporte de Turno (PDF)"):
                gr.Markdown("### Generar Reporte de Cierre de Turno / Dia")
                gr.Markdown("Haga clic en el boton para compilar todos los registros actuales en un PDF listo para descargar.")
                
                boton_pdf = gr.Button("Generar PDF de Registros", variant="primary")
                archivo_pdf = gr.File(label="Descargar Reporte PDF")

                boton_pdf.click(
                    generar_pdf_turno,
                    outputs=archivo_pdf
                )


    # ==================== LÓGICA DE NAVEGACIÓN ====================
    btn_ir_admin.click(
        fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
        outputs=[pantalla_portada, pantalla_admin]
    )

    btn_volver_portada.click(
        fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[pantalla_portada, pantalla_admin]
    )

import os

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))