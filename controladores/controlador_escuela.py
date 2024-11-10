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
                ORDER BY e.nombre
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

# Función para obtener facultades
def obtener_facultades():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    facultades = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idFacultad, nombre FROM facultad")
            rows = cursor.fetchall()
            for row in rows:
                facultad_dict = {"idFacultad": row[0], "nombre": row[1]}
                facultades.append(facultad_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return facultades

# Función para obtener los datos de una escuela por ID
def obtener_escuela_por_id(idEscuela):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute(""" 
                SELECT e.idEscuela, e.nombre, e.abreviatura, e.estado, 
                f.idFacultad, f.nombre AS facultad, h.hRequeridas
                FROM escuela e
                INNER JOIN facultad f ON e.idFacultad = f.idFacultad
                INNER JOIN horas_ppp h ON e.idHoras = h.idHoras
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

#
def obtener_escuela_por_id_modificar(idEscuela):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM escuela WHERE idEscuela = %s", (idEscuela,))
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

# Agregar una nueva escuela
def agregar_escuela(nombre, abreviatura, estado, idFacultad, hRequeridas):
    # Validar que hRequeridas es un número válido
    try:
        hRequeridas = int(hRequeridas)  # Intentamos convertir hRequeridas a un entero
    except ValueError:
        return {"error": "El valor de las horas requeridas debe ser un número válido."}

    # Validar que hRequeridas sea mayor que cero
    if hRequeridas <= 0:
        return {"error": "Las horas requeridas deben ser un número mayor a cero."}

    # Validar que idFacultad existe en la base de datos
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Validar que idFacultad existe en la tabla facultad
            cursor.execute("SELECT COUNT(*) FROM facultad WHERE idFacultad = %s", (idFacultad,))
            if cursor.fetchone()[0] == 0:
                return {"error": f"No existe una facultad con id {idFacultad}."}

            # Insertar la nueva escuela
            cursor.execute("""
                INSERT INTO escuela (nombre, abreviatura, estado, idFacultad, hRequeridas)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, abreviatura, estado, idFacultad, hRequeridas))

            conexion.commit()
            return {"mensaje": "Escuela agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": f"Error en la base de datos: {str(e)}"}  # Mostrar el error exacto de la base de datos
    finally:
        conexion.close()

# Modificar una escuela
def modificar_escuela(idEscuela, nombre, abreviatura, estado, idFacultad, hRequeridas):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Comprobamos que la facultad existe
            cursor.execute("SELECT COUNT(*) FROM facultad WHERE idFacultad = %s", (idFacultad,))
            if cursor.fetchone()[0] == 0:
                return {"error": f"No existe una facultad con id {idFacultad}."}

            # Realizamos la actualización
            cursor.execute("""
                UPDATE escuela
                SET nombre = %s, abreviatura = %s, estado = %s, idFacultad = %s, hRequeridas = %s
                UPDATE escuela
                SET nombre = %s, abreviatura = %s, estado = %s, idFacultad = %s, hRequeridas = %s
                WHERE idEscuela = %s
            """, (nombre, abreviatura, estado, idFacultad, hRequeridas, idEscuela))
            
            conexion.commit()  # Confirmar los cambios en la base de datos
            print("Escuela modificada correctamente")  # Asegúrate de que la actualización se realizó
            return {"mensaje": "Escuela modificada correctamente"}

    except Exception as e:
        conexion.rollback()  # Si algo falla, revertir los cambios
        print(f"Error al modificar la escuela: {str(e)}")  # Log de error
        return {"error": f"Error al modificar la escuela: {str(e)}"}
    finally:
        conexion.close()


# Eliminar una escuela
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