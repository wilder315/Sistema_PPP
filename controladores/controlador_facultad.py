from bd import obtener_conexion

def obtener_facultades():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}   
    facultades = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM facultad")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                facultad_dict = dict(zip(column_names, row))
                facultades.append(facultad_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()    
    return facultades

def obtener_facultad_por_id(idFacultad):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM facultad WHERE idFacultad = %s", (idFacultad,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                facultad_dict = dict(zip(columnas, row))
                return facultad_dict
            else:
                return {"error": "Facultad no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_facultad(nombre, abreviatura, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO facultad (nombre, abreviatura, estado) 
                VALUES (%s, %s, %s)
            """, (nombre, abreviatura, estado))
            conexion.commit()
            return {"mensaje": "Facultad agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_facultad(idFacultad, nombre, abreviatura, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE facultad 
                SET nombre = %s, abreviatura = %s, estado = %s 
                WHERE idFacultad = %s
            """, (nombre, abreviatura, estado, idFacultad))
            conexion.commit()
            return {"mensaje": "Facultad modificada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_facultad(idFacultad):
    if not idFacultad:
        return {"error": "El ID de la facultad es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM escuela
                WHERE idFacultad = %s
            """, (idFacultad,))
            referencia = cursor.fetchone()[0]          
            if referencia > 0:
                return {"error": "No se puede eliminar una facultad en uso."}
            cursor.execute("DELETE FROM facultad WHERE idFacultad = %s", (idFacultad,))
            conexion.commit()
            return {"mensaje": "Facultad eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_facultad(idFacultad):
    if not idFacultad:
        return {"error": "El ID de la facultad es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE facultad SET estado = 'I' WHERE idFacultad = %s", (idFacultad,))
            conexion.commit()
            return {"mensaje": "Facultad dada de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()