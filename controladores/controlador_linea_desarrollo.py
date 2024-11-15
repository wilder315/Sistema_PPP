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

def obtener_linea_desarrollo_por_id(idLinea):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM linea_desarrollo WHERE idLinea = %s", (idLinea,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                linea_desarrollo_dict = dict(zip(columnas, row))
                return linea_desarrollo_dict
            else:
                return {"error": "Facultad no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()


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

def modificar_linea_desarrollo(idLinea, nombre, estado, idEscuela):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE linea_desarrollo 
                SET nombre = %s, estado = %s, idEscuela = %s 
                WHERE idLinea = %s
            """, (nombre, estado, idEscuela, idLinea))
            conexion.commit()
            return {"mensaje": "Línea de desarrollo modificada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_linea_desarrollo(idLinea):
    if not idLinea:
        return {"error": "El ID de la Línea es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM linea_desarrollo WHERE idLinea = %s", (idLinea,))
            conexion.commit()
            return {"mensaje": "Linea de desarrollo eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_linea_desarrollo(idLinea):
    if not idLinea:
        return {"error": "El ID de la Línea es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE linea_desarrollo SET estado = 'I' WHERE idLinea = %s", (idLinea,))
            conexion.commit()
            return {"mensaje": "Línea de desarrollo dado de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()