from datetime import datetime, timedelta
from conexion import get_connection
from main import menu_inicio

def pantalla_arrepentimiento():
    print("""
    --- BOTÓN DE ARREPENTIMIENTO ---
    """)
    
    print("Escriba 'salir' para volver al menú principal")
    email = input("Ingrese el email del cliente para consultar sus ventas: ")
    if email.lower() == "salir":
        menu_inicio()
        return

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Consulta las ventas del cliente según su email
        query = """
        SELECT v.id_venta, c.email, v.id_destino, he.fecha, ev.nombre 
        FROM VENTA v
        INNER JOIN CLIENTE c ON v.id_cliente = c.id_cliente
        INNER JOIN (
            SELECT id_venta, MAX(fecha) AS fecha
            FROM HISTORIAL_ESTADOVENTA
            GROUP BY id_venta
        ) ult_he ON v.id_venta = ult_he.id_venta
        INNER JOIN HISTORIAL_ESTADOVENTA he ON v.id_venta = he.id_venta AND he.fecha = ult_he.fecha
        INNER JOIN ESTADO_VENTA ev ON he.id_estado = ev.id_estado
        WHERE c.email = %s
        ORDER BY he.fecha DESC
        """
        cursor.execute(query, (email,))
        ventas = cursor.fetchall()

        # Si no hay ventas, mostrar mensaje y solicitar nuevamente el email
        if not ventas:
            print("No se encontraron ventas asociadas a este cliente.")
            pantalla_arrepentimiento()
            return

        # Agrupa las ventas para mostrar una sola por ID
        ventas_dict = {}
        for v in ventas:
            id_venta = v[0]
            if id_venta not in ventas_dict:
                estado = v[4]
                fecha_estado = v[3]
                ventas_dict[id_venta] = {
                    "email": v[1],
                    "id_destino": v[2],
                    "fecha_estado": fecha_estado,
                    "estado": estado
                }

        print("\nVentas encontradas:")
        for idx, (id_venta, datos) in enumerate(ventas_dict.items(), start=1):
            print(f"{idx}. ID Venta: {id_venta}, Destino ID: {datos['id_destino']}, Estado: {datos['estado']}, Fecha estado: {datos['fecha_estado']}")

        seleccion_input = input("\nSeleccione el número de la venta que desea revisar: ")
        if seleccion_input.lower() == "salir":
            menu_inicio()
            return

        seleccion = int(seleccion_input)
        id_venta_seleccionada = list(ventas_dict.keys())[seleccion - 1]
        venta_seleccionada = ventas_dict[id_venta_seleccionada]

        estado_actual = venta_seleccionada["estado"]
        fecha_estado = venta_seleccionada["fecha_estado"]

        # Si el estado es pendiente y dentro del plazo de 5 minutos, permite cancelar
        if estado_actual.lower() == "pendiente":
            tiempo_actual = datetime.now()
            diferencia = tiempo_actual - fecha_estado

            if diferencia <= timedelta(minutes=5):
                print("\n¿Está usted seguro? Si continúa, su venta será cancelada.")
                print("1 - Continuar con la cancelación")
                print("2 - Cancelar y volver")

                opcion = input("Ingrese una opción: ")

                if opcion == "1":
                    update_query = """
                    INSERT INTO HISTORIAL_ESTADOVENTA (id_venta, id_estado, fecha)
                    VALUES (%s, %s, NOW())
                    """
                    cursor.execute(update_query, (id_venta_seleccionada, 3))
                    connection.commit()
                    print("La venta ha sido cancelada exitosamente.")
                    menu_inicio()
                    return
                else:
                    print("Operación cancelada por el usuario.")
                    menu_inicio()
                    return
        else:
            print("\nUsted ha sobrepasado el tiempo estipulado para cancelación/arrepentimiento.")
            print("Por favor, comuníquese con la compañía para gestionar un cambio.")
            print("0800-000000 Atención al cliente de SkyRoute, de Lunes a Viernes de 09 a 18 hs.")
            print("\n1 - Volver al menú principal")
            print("2 - Salir del sistema")
            opcion = input("Ingrese una opción: ")
            if opcion == "1":
                menu_inicio()
                return
            else:
                return

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        menu_inicio()
        return
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    pantalla_arrepentimiento()
