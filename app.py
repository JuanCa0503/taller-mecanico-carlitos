import os
import libsql
import gradio as gr

# ==================== CONFIGURACIÓN DE TURSO ====================
# Reemplaza con los valores de tu base de datos si es necesario
TURSO_URL = "https://tallermecanico-car-rex05.aws-us-west-2.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3ODk5NTI2MTcsImlkIjoiMDFhMDU4NzEtM2YwMS03ODFkLWIwNzgtM2QxMTRhOGJlYTJlIiwia2lkIjoiLXl6VE9OdUtMY0QtSkxmSFVHUkJ1RjQ5SEtmMFJtbEZVMHRkWnB5SUgzOCIsInJpZCI6IjJiMWU3Mjc2LTRmZWQtNGZhOS1hZWI0LWI0YmZiMzBhMDc1NiJ9._3Bh47awuLjcVsdJLqUVMsdngY9YgCi111jWCSfY3LcDDb3etPvxx8pXTHRmg_dudgZRDgvQlTYU2Jd-c8_TDQ"

def conectar_db():
    return libsql.connect("taller.db", sync_url=TURSO_URL, auth_token=TURSO_TOKEN)

# ==================== FUNCIONES DEL SISTEMA ====================

# 1. Obtener catálogo para el cliente
def obtener_catalogo_cliente():
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, descripcion, precio, imagen_url FROM productos")
        filas = cursor.fetchall()
        conn.close()
        # Retorna los datos organizados para mostrarlos en la tabla
        return [[f[0], f[1], f[2], f"${f[3]:.2f}", f[4]] for f in filas]
    except Exception as e:
        return []

# 2. Agregar un nuevo producto (Admin)
def agregar_producto(nombre, descripcion, precio, imagen_url):
    if not nombre or precio <= 0:
        return "⚠️ Error: Ingresa un nombre válido y un precio mayor a 0."
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, imagen_url) VALUES (?, ?, ?, ?)",
            (nombre, descripcion, precio, imagen_url)
        )
        conn.commit()
        conn.close()
        return "✅ Producto agregado correctamente al catálogo."
    except Exception as e:
        return f"⚠️ Error al conectar con la base de datos: {e}"

# 3. Modificar precio de un producto existente (Admin)
def actualizar_precio(producto_id, nuevo_precio):
    if producto_id <= 0 or nuevo_precio <= 0:
        return "⚠️ Error: ID y precio deben ser mayores a 0."
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET precio = ? WHERE id = ?",
            (nuevo_precio, producto_id)
        )
        conn.commit()
        conn.close()
        return "✅ Precio actualizado con éxito."
    except Exception as e:
        return f"⚠️ Error al actualizar: {e}"

# ==================== INTERFAZ DE GRADIO ====================

custom_css = """
body { background-color: #1a1a2e; color: #ffffff; }
"""

with gr.Blocks(title="Taller Mecánico Carlitos", css=custom_css) as app:
    
    # ---------------- VISTA DEL CLIENTE (PORTADA) ----------------
    with gr.Column(visible=True) as pantalla_portada:
        gr.Markdown("# 🛠️ Taller Mecánico Carlitos")
        gr.Markdown("Sistema integral de control automotriz, servicios e inventario.")
        
        gr.Markdown("## 📦 Catálogo de Productos y Servicios")
        gr.Markdown("Consulta nuestros repuestos y accesorios disponibles:")
        
        # Tabla interactiva en modo solo lectura para el cliente
        catalogo_tabla = gr.Dataframe(
            headers=["ID", "Producto", "Descripción", "Precio", "Imagen (URL)"],
            datatype=["number", "str", "str", "str", "str"],
            interactive=False, # Impide que el cliente edite
            value=obtener_catalogo_cliente
        )
        
        btn_actualizar_catalogo = gr.Button("🔄 Actualizar Catálogo")
        btn_actualizar_catalogo.click(fn=obtener_catalogo_cliente, outputs=catalogo_tabla)
        
        with gr.Row():
            btn_ir_admin = gr.Button("Panel de Administrador", variant="primary")

    # ---------------- VISTA DEL ADMINISTRADOR ----------------
    with gr.Column(visible=False) as pantalla_admin:
        gr.Markdown("# ⚙️ Panel de Control - Administrador")
        
        with gr.Tabs():
            with gr.Tab("Agregar Nuevo Producto"):
                txt_nombre = gr.Textbox(label="Nombre del Producto")
                txt_desc = gr.Textbox(label="Descripción")
                num_precio = gr.Number(label="Precio ($)")
                txt_img_url = gr.Textbox(label="URL de la Imagen (opcional)")
                
                btn_guardar = gr.Button("Guardar Producto", variant="primary")
                lbl_resultado = gr.Textbox(label="Estado", interactive=False)
                
                btn_guardar.click(
                    fn=agregar_producto,
                    inputs=[txt_nombre, txt_desc, num_precio, txt_img_url],
                    outputs=lbl_resultado
                )

            with gr.Tab("Modificar Precios"):
                num_id_prod = gr.Number(label="ID del Producto a modificar", precision=0)
                num_nuevo_precio = gr.Number(label="Nuevo Precio ($)")
                
                btn_actualizar = gr.Button("Actualizar Precio", variant="primary")
                lbl_resultado_precio = gr.Textbox(label="Estado", interactive=False)
                
                btn_actualizar.click(
                    fn=actualizar_precio,
                    inputs=[num_id_prod, num_nuevo_precio],
                    outputs=lbl_resultado_precio
                )

        btn_volver_portada = gr.Button("⬅️ Volver al Catálogo (Cliente)")

    # ---------------- NAVEGACIÓN ENTRE PANTALLAS ----------------
    btn_ir_admin.click(
        fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
        outputs=[pantalla_portada, pantalla_admin]
    )
    
    btn_volver_portada.click(
        fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
        outputs=[pantalla_portada, pantalla_admin]
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))