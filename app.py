import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("https://cngsfkwkaodbopikrplm.supabase.co"),
    os.getenv("sb_publishable_ZByXGOuhARBXw_0w_xbN3w_qld1NU2P")
)

def registrar_venta_completa(cliente_id, lista_items, forma_pago, total_venta):
    """
    Crea un pedido, agrega sus detalles y registra el pago en Supabase.
    """
    try:
        # 1. Crear el Pedido
        pedido_res = supabase.table("pedidos").insert({
            "cliente_id": cliente_id,
            "estado": "Completado",
            "total": total_venta
        }).execute()
        
        pedido_id = pedido_res.data[0]["id"]

        # 2. Registrar los detalles del pedido (autopartes vendidas)
        for item in lista_items:
            supabase.table("detalle_pedido").insert({
                "pedido_id": pedido_id,
                "autoparte_id": item["autoparte_id"],
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"]
            }).execute()

        # 3. Registrar el Pago
        supabase.table("pagos").insert({
            "pedido_id": pedido_id,
            "monto": total_venta,
            "forma_pago": forma_pago # "Efectivo", "Tarjeta", etc.
        }).execute()

        print(f"¡Venta registrada con éxito! Pedido ID: {pedido_id}")

    except Exception as e:
        print("Error al procesar la venta:", e)

# Ejemplo de prueba:
# registrar_venta_completa(
#     cliente_id=1, 
#     lista_items=[{"autoparte_id": 1, "cantidad": 2, "precio_unitario": 250.00}], 
#     forma_pago="Tarjeta de Crédito", 
#     total_venta=500.00
# )
