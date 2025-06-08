from datetime import datetime, timedelta
from conexion import get_connection

def pantalla_arrepentimiento():
    print("""
    --- BOTÓN DE ARREPENTIMIENTO ---
    """)

    email = input("Ingrese el email del cliente para consultar sus ventas: ")

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Consulta las ventas asociadas a ese email
        query = """
        SELECT v.id_venta, c.email, v.id_destino, he.fecha, ev.nombre 
        FROM VENTA v
        INNER JOIN CLIENTE c ON v.id_cliente = c.id_cliente
        INNER JOIN HISTORIAL_ESTADOVENTA he ON v.id_venta = he.id_venta
        INNER JOIN ESTADO_VENTA ev ON he.id_estado = ev.id_estado
        WHERE c.email = %s
        ORDER BY he.fecha DESC
        """
        cursor.execute(query, (email,))
        ventas = cursor.fetchall()

        if not ventas:
            print("No se encontraron ventas asociadas a este cliente.")
            return

        # Agrupar por ID de venta para evitar repeticiones si hay múltiples estados
        ventas_dict = {}
        for v in ventas:
            id_venta = v[0]
            if id_venta not in ventas_dict:
                ventas_dict[id_venta] = {
                    "email": v[1],
                    "id_destino": v[2],
                    "fecha_estado": v[3],
                    "estado": v[4]
                }

        # Mostrar ventas únicas
        print("\nVentas encontradas:")
        for idx, (id_venta, datos) in enumerate(ventas_dict.items(), start=1):
            print(f"{idx}. ID Venta: {id_venta}, Destino ID: {datos['id_destino']}, Estado: {datos['estado']}, Fecha estado: {datos['fecha_estado']}")

        seleccion = int(input("\nSeleccione el número de la venta que desea revisar: "))
        id_venta_seleccionada = list(ventas_dict.keys())[seleccion - 1]
        venta_seleccionada = ventas_dict[id_venta_seleccionada]

        estado_actual = venta_seleccionada["estado"]
        fecha_estado = venta_seleccionada["fecha_estado"]

        if estado_actual.lower() == "pendiente":
            tiempo_actual = datetime.now()
            tiempo_estado = datetime.combine(fecha_estado, datetime.min.time())
            diferencia = tiempo_actual - tiempo_estado

            if diferencia <= timedelta(minutes=5):
                print("\n¿Está usted seguro? Si continúa, su venta será cancelada.")
                print("1 - Continuar con la cancelación")
                print("2 - Cancelar y volver")

                opcion = input("Ingrese una opción: ")

                if opcion == "1":
                    # Cambiar estado a 'Anulada'
                    update_query = """
                    INSERT INTO HISTORIAL_ESTADOVENTA (id_venta, id_estado, fecha)
                    VALUES (%s, %s, NOW())
                    """
                    cursor.execute(update_query, (id_venta_seleccionada, 3))  # Estado 3 = Anulada
                    connection.commit()
                    print("La venta ha sido cancelada exitosamente.")
                else:
                    print("Operación cancelada por el usuario.")
            else:
                print("\nUsted ha sobrepasado el tiempo estipulado para cancelación/arrepentimiento.")
                print("Por favor, comuníquese con la compañía para gestionar un cambio.")
                print("0800-000000 Atención al cliente de SkyRoute, de Lunes a Viernes de 09 a 18 hs.")
                print("\n1 - Volver al menú principal")
                print("2 - Salir del sistema")
        else:
            print(f"La venta seleccionada no está en estado 'Pendiente' (estado actual: {estado_actual}).")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    pantalla_arrepentimiento()
