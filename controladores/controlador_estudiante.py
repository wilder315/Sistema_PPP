from bd import obtener_conexion

def obtener_estudiantes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    estudiantes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.codUniversitario, p.tel1, p.tel2, 
                       p.correoP, p.correoUSAT, p.estado, g.nombre as genero, td.nombre as tipoDocumento, 
                       e.nombre as escuela, u.username as usuario
                FROM persona p
                LEFT JOIN genero g ON p.idGenero = g.idGenero
                LEFT JOIN tipo_documento td ON p.idTipoDoc = td.idTipoDoc
                LEFT JOIN escuela e ON p.idEscuela = e.idEscuela
                LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE u.idTipoUsuario = 3
                ORDER BY p.apellidos ASC, p.nombre ASC 
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                estudiante_dict = dict(zip(column_names, row))
                estudiantes.append(estudiante_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return estudiantes

def obtener_estudiante_por_id(idEstudiante):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.codUniversitario, p.tel1, p.tel2, 
                       p.correoP, p.correoUSAT, p.estado, p.idGenero, p.idTipoDoc, 
                        p.idEscuela, p.idUsuario
                FROM persona p
                WHERE p.idPersona = %s
            """, (idEstudiante,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                estudiante_dict = dict(zip(columnas, row))
                return estudiante_dict
            else:
                return {"error": "Estudiante no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_estudiante_por_id_modificar(idEstudiante):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.codUniversitario, p.tel1, p.tel2, 
                       p.correoP, p.correoUSAT, p.estado, p.idGenero, p.idTipoDoc, 
                        p.idEscuela, p.idUsuario
                FROM persona p
                WHERE p.idPersona = %s
            """, (idEstudiante,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                estudiante_dict = dict(zip(columnas, row))
                return estudiante_dict
            else:
                return {"error": "Estudiante no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_estudiante(numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela):
    if not tel2:
        tel2 = None
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO persona (numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela))
            conexion.commit()
            return {"mensaje": "Estudiante agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_estudiante(idEstudiante, numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela):
    if not tel2:
        tel2 = None
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE persona
                SET numDoc = %s, nombre = %s, apellidos = %s, codUniversitario = %s, tel1 = %s, tel2 = %s, 
                    correoP = %s, correoUSAT = %s, estado = %s, idGenero = %s, idTipoDoc = %s, 
                    idUsuario = %s, idEscuela = %s
                WHERE idPersona = %s
            """, (numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela, idEstudiante))
            conexion.commit()
            return {"mensaje": "Estudiante modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_estudiante(idEstudiante):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM persona WHERE idPersona = %s", (idEstudiante,))
            conexion.commit()
            return {"mensaje": "Estudiante eliminado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_estudiante(idEstudiante):
    if not idEstudiante:
        return {"error": "El ID del estudiante es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idEstudiante,))
            conexion.commit()
            return {"mensaje": "Estudiante dado de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()