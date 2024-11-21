from bd import obtener_conexion

def obtener_generos():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    generos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM genero")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                genero_dict = dict(zip(column_names, row))
                generos.append(genero_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return generos

def obtener_genero_por_id(idGenero):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM genero WHERE idGenero = %s", (idGenero,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                genero_dict = dict(zip(columnas, row))
                return genero_dict
            else:
                return {"error": "Genero no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_genero(nombre, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO genero (nombre, estado) 
                VALUES (%s, %s)
            """, (nombre, estado))
            conexion.commit()
            return {"mensaje": "Genero agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_genero(idGenero, nombre, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE genero 
                SET nombre = %s, estado = %s 
                WHERE idGenero = %s
            """, (nombre, estado, idGenero))
            conexion.commit()
            return {"mensaje": "Genero modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_genero(idGenero):
    if not idGenero:
        return {"error": "El ID del género es requerido."}    
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}   
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*)
                FROM persona
                WHERE idGenero = %s
            """, (idGenero,))
            referencia_persona = cursor.fetchone()[0]     
            if referencia_persona > 0:
                return {"error": "No se puede eliminar un género en uso."}
            cursor.execute("DELETE FROM genero WHERE idGenero = %s", (idGenero,))
            conexion.commit()
            return {"mensaje": "Género eliminado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_genero(idGenero):
    if not idGenero:
        return {"error": "El ID del genero es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE genero SET estado = 'I' WHERE idGenero = %s", (idGenero,))
            conexion.commit()
            return {"mensaje": "Genero dado de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()