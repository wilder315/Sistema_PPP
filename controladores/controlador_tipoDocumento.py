from bd import obtener_conexion

def obtener_tipoDocumento():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    tipoDocumentos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM tipo_documento")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                tipoDocumento_dict = dict(zip(column_names, row))
                tipoDocumentos.append(tipoDocumento_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return tipoDocumentos