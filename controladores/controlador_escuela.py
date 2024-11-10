from bd import obtener_conexion

def obtener_escuelas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    escuelas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT e.idEscuela, e.nombre, e.abreviatura, e.estado, 
                       f.nombre AS facultad, e.hRequeridas 
                FROM escuela e 
                INNER JOIN facultad f ON e.idFacultad = f.idFacultad 
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                escuela_dict = dict(zip(column_names, row))
                escuelas.append(escuela_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()   
    return escuelas

def obtener_escuela_por_id(idEscuela):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute(""" 
                SELECT e.idEscuela, e.nombre, e.abreviatura, e.estado, 
                       f.idFacultad, f.nombre AS facultad, e.hRequeridas
                FROM escuela e
                WHERE e.idEscuela = %s
            """, (idEscuela,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                escuela_dict = dict(zip(columnas, row))
                return escuela_dict
            else:
                return {"error": "Escuela no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_escuela(nombre, abreviatura, estado, idFacultad, hRequeridas):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO escuela (nombre, abreviatura, estado, idFacultad, hRequeridas)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, abreviatura, estado, idFacultad, hRequeridas))
            conexion.commit()
            return {"mensaje": "Escuela agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_escuela(idEscuela, nombre, abreviatura, estado, idFacultad, hRequeridas):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE escuela
                SET nombre = %s, abreviatura = %s, estado = %s, idFacultad = %s, hRequeridas = %s
                WHERE idEscuela = %s
            """, (nombre, abreviatura, estado, idFacultad, hRequeridas, idEscuela))
            conexion.commit()
            return {"mensaje": "Escuela modificada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_escuela(idEscuela):
    if not idEscuela:
        return {"error": "El ID de la escuela es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM escuela WHERE idEscuela = %s", (idEscuela,))
            conexion.commit()
            return {"mensaje": "Escuela eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_escuela(idEscuela):
    if not idEscuela:
        return {"error": "El ID de la escuela es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE escuela SET estado = 'I' WHERE idEscuela = %s", (idEscuela,))
            conexion.commit()
            return {"mensaje": "Escuela dada de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()