from bd import obtener_conexion

def obtener_lineas_desarrollo():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    lineas_desarrollo = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM linea_desarrollo ORDER BY nombre")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                linea_desarrollo_dict = dict(zip(column_names, row))
                lineas_desarrollo.append(linea_desarrollo_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return lineas_desarrollo


def agregar_linea_desarrollo(nombre, estado, idEscuela):
    #validaciones 
    if not nombre or not estado or not idEscuela: 
        return {"error": "Todos los campos son requeridos."}

    conexion = obtener_conexion() 
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try: 
        with conexion.cursor() as cursor:  
            cursor.execute("""
                INSERT INTO linea_desarrollo (nombre, estado, idEscuela)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, estado, idEscuela))
            conexion.commit()
            return {"mensaje": "Plan trabajo agregado correctamente"}
    except Exception as e: 
        conexion.rollback()
        return {"error": str(e)}
    finally: 
        conexion.close()
