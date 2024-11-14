from bd import obtener_conexion

def obtener_objetivos():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    objetivos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM objetivos")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                objetivos_dict = dict(zip(column_names, row))
                objetivos.append(objetivos_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return objetivos

def agregar_objetivos(descripcion, idInforme):
    #validaciones 
    if not descripcion or not idInforme: 
        return {"error": "Todos los campos son requeridos."}

    conexion = obtener_conexion() 
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try: 
        with conexion.cursor() as cursor:  
            cursor.execute("""
                INSERT INTO objetivos (descripcion, idInforme)
                VALUES (%s, %s)
            """, (descripcion, idInforme))
            conexion.commit()
            return {"mensaje": "objetivo agregado correctamente"}
    except Exception as e: 
        conexion.rollback()
        return {"error": str(e)}
    finally: 
        conexion.close()