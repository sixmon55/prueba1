from datetime import datetime
from conexion import get_connection

def menu_ventas(menu_inicio):
    while True:
        print("\n--- Gestión de Ventas ---")
        print("1. Registrar nueva venta")
        print("2. Consultar ventas por cliente")
        print("3. Informe de ventas")
        print("4. Cerrar")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_nueva_venta()
        elif opcion == "2":
            consultar_ventas_cliente()
        elif opcion == "3":
            informe_ventas()
        elif opcion == "4":
            menu_inicio()
            return
        else:
            print("Opción inválida. Intente nuevamente.")

def registrar_nueva_venta():
    conn = get_connection()
    cursor = conn.cursor()

    while True:
        email = input("Ingrese el correo electrónico del cliente (o escriba 'salir' para cerrar): ").strip()
        if email.lower() == "salir":
            return

        cursor.execute("SELECT id_cliente, razon_social FROM CLIENTE WHERE email = %s", (email,))
        cliente = cursor.fetchone()

        if cliente:
            id_cliente, razon_social = cliente
            print(f"\nCliente encontrado: {razon_social} (ID: {id_cliente})\n")
            break
        else:
            print("No se encontró un cliente con ese correo. Intente nuevamente.\n")

    while True:
        cursor.execute("""
            SELECT D.id_destino, C.nombre, P.nombre, D.costo_base
            FROM DESTINO D
            JOIN CIUDAD C ON D.id_ciudad = C.id_ciudad
            JOIN PAIS P ON C.id_pais = P.id_pais
        """)
        destinos = cursor.fetchall()

        print("\nSeleccione un destino para la venta:\n")
        for i, destino in enumerate(destinos, start=1):
            id_destino, ciudad, pais, costo = destino
            print(f"{i}. {ciudad}, {pais} - Costo base: ${costo:.2f}")
        print("0. Volver atrás")

        try:
            opcion = int(input("\nIngrese el número de la opción: "))
        except ValueError:
            print("Por favor, ingrese un número válido.")
            continue

        if opcion == 0:
            return
        elif 1 <= opcion <= len(destinos):
            destino_seleccionado = destinos[opcion - 1]
            id_destino = destino_seleccionado[0]
            ciudad = destino_seleccionado[1]
            pais = destino_seleccionado[2]
            costo = destino_seleccionado[3]

            print(f"\nDestino seleccionado: {ciudad}, {pais} - ${costo:.2f}")

            confirmar = input("¿Está seguro que desea registrar esta venta?\n1 - Sí, continuar\n2 - No, volver atrás\nIngrese opción: ")

            if confirmar == "1":
                try:
                    cursor.execute("""
                        INSERT INTO VENTA (id_cliente, id_destino)
                        VALUES (%s, %s)
                    """, (id_cliente, id_destino))
                    conn.commit()

                    id_venta = cursor.lastrowid
                    fecha_actual = datetime.now()

                    cursor.execute("""
                        INSERT INTO HISTORIAL_ESTADOVENTA (id_venta, id_estado, fecha)
                        VALUES (%s, %s, %s)
                    """, (id_venta, 1, fecha_actual))  # Estado 1 = Pendiente
                    conn.commit()

                    print("\n✅ Venta registrada exitosamente.")
                    return

                except Exception as e:
                    print("Error al registrar la venta:", e)
                    conn.rollback()
                    return

            elif confirmar == "2":
                continue
            else:
                print("Opción no válida. Volviendo al listado de destinos.\n")
                continue
        else:
            print("Opción inválida. Intente nuevamente.\n")

def consultar_ventas_cliente():
    conn = get_connection()
    cursor = conn.cursor()

    email = input("Ingrese el correo electrónico del cliente o escriba 'salir' para volver atrás: ").strip()
    if email.lower() == "salir":
        return

    cursor.execute("SELECT id_cliente, razon_social FROM CLIENTE WHERE email = %s", (email,))
    cliente = cursor.fetchone()

    if not cliente:
        print("No se encontró un cliente con ese correo.")
        return

    id_cliente, razon_social = cliente
    print(f"\nVentas del cliente: {razon_social}")

    cursor.execute("""
        SELECT V.id_venta, C.nombre, P.nombre, D.costo_base, HV.fecha, HV.id_estado
        FROM VENTA V
        JOIN DESTINO D ON V.id_destino = D.id_destino
        JOIN CIUDAD C ON D.id_ciudad = C.id_ciudad
        JOIN PAIS P ON C.id_pais = P.id_pais
        JOIN (
            SELECT id_venta, MAX(fecha) as max_fecha
            FROM HISTORIAL_ESTADOVENTA
            GROUP BY id_venta
        ) ult_estado ON V.id_venta = ult_estado.id_venta
        JOIN HISTORIAL_ESTADOVENTA HV ON HV.id_venta = ult_estado.id_venta AND HV.fecha = ult_estado.max_fecha
        WHERE V.id_cliente = %s
        ORDER BY V.id_venta DESC
    """, (id_cliente,))

    ventas = cursor.fetchall()

    if not ventas:
        print("No hay ventas registradas para este cliente.")
        return

    for venta in ventas:
        id_venta, ciudad, pais, costo, fecha, id_estado = venta

        if id_estado == 3:
            estado = "Anulado"
        elif id_estado == 1:
            if (datetime.now() - fecha).total_seconds() / 60 <= 5:
                estado = "Pendiente"
            else:
                estado = "Completado"
        elif id_estado == 2:
            estado = "Completado"
        else:
            estado = f"Estado desconocido ({id_estado})"

        print(f"\nID Venta: {id_venta}")
        print(f"Destino: {ciudad}, {pais}")
        print(f"Costo: ${costo:.2f}")
        print(f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Estado actual: {estado}")

def informe_ventas():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT V.id_venta, CL.razon_social, C.nombre, P.nombre, D.costo_base, HV.fecha, HV.id_estado
        FROM VENTA V
        JOIN CLIENTE CL ON V.id_cliente = CL.id_cliente
        JOIN DESTINO D ON V.id_destino = D.id_destino
        JOIN CIUDAD C ON D.id_ciudad = C.id_ciudad
        JOIN PAIS P ON C.id_pais = P.id_pais
        JOIN (
            SELECT id_venta, MAX(fecha) as max_fecha
            FROM HISTORIAL_ESTADOVENTA
            GROUP BY id_venta
        ) ult_estado ON V.id_venta = ult_estado.id_venta
        JOIN HISTORIAL_ESTADOVENTA HV ON HV.id_venta = ult_estado.id_venta AND HV.fecha = ult_estado.max_fecha
        ORDER BY V.id_venta DESC
    """)
    ventas = cursor.fetchall()

    if not ventas:
        print("No hay ventas registradas.")
        return

    print("\n--- Informe de todas las ventas ---")
    for venta in ventas:
        id_venta, cliente, ciudad, pais, costo, fecha, id_estado = venta
        if id_estado == 3:
            estado = "Anulado"
        elif id_estado == 1 and (datetime.now() - fecha).total_seconds() / 60 <= 5:
            estado = "Pendiente"
        else:
            estado = "Completado"

        print(f"\nID Venta: {id_venta}")
        print(f"Cliente: {cliente}")
        print(f"Destino: {ciudad}, {pais}")
        print(f"Costo: ${costo:.2f}")
        print(f"Fecha: {fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Estado actual: {estado}")
