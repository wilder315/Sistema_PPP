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
