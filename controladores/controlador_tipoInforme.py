from bd import obtener_conexion

def obtener_tipo_informe():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    tipo_informe = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM tipo_informe")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                tipo_informe_dict = dict(zip(column_names, row))
                tipo_informe.append(tipo_informe_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return tipo_informe


