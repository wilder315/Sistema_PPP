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
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idEstudiante,))
            conexion.commit()
            return {"mensaje": "Estudiante dado de baja correctamente"}
            return {"mensaje": "Estudiante dado de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

# OTRAS OPERACIONES
def obtener_estudiantes_activas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS estudiantes_activas FROM estudiante WHERE estado = 'A'")
            row = cursor.fetchone()

            if row:
                return {"estudiantes_activas": row[0]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_estudiantes_con_estado():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    estudiantes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    idEstudiante, 
                    nombre, 
                    CASE 
                        WHEN estado = 'A' THEN 'Activo' 
                        ELSE 'Inactivo' 
                    END AS estado 
                FROM estudiante 
                ORDER BY nombre
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

#Carlos Delgado 9-11-2024
def obtener_estudiantes_por_fecha(): 
    conexion = obtener_conexion()
    if not conexion:
        return {"Error": "No se puedo establecer conexión con la base de datos."}
    
    registros_por_fecha = []
    try: 
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(pp.idSemestre) as total_id, sa.nombre as nombre
                FROM practicas_preprofesionales as pp
                INNER JOIN semestre_academico as sa on pp.idSemestre = sa.idSemestre
                GROUP BY sa.nombre
                """)
            rows = cursor.fetchall()
            
            registros_por_fecha = [{"total_id": row[0], "nombre": row[1]} for row in rows]
            
            
    except Exception as e:
        print("Error al obtener los datos:" ,e)
        return []
    finally:
        conexion.close()
        
    return registros_por_fecha

def obtener_estadisticas_estudiantes(): 
    conexion = obtener_conexion()
    if not conexion:
        return {"Error": "No se puedo establecer conexión con la base de datos."}
    
    estadisticas = {}
    try: 
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                (SELECT COUNT(*) FROM practicas_preprofesionales) AS registrados,
                (SELECT COUNT(*) FROM practicas_preprofesionales where idEstado = 2) AS proceso,
                (SELECT COUNT(*) FROM practicas_preprofesionales where idEstado = 3) AS espera_informes, 
                (SELECT COUNT(*) FROM practicas_preprofesionales where idEstado = 4) AS finalizada
                """  
            )
            #obtener los resultados
            resultado = cursor.fetchone()
            
            # asignar los resultados a un diccionario simple
            estadisticas = {
                "registrados": resultado[0], 
                "proceso": resultado[1], 
                "espera_informes": resultado[2], 
                "finalizada": resultado[3]
            }
            
    except Exception as e:
        print("Error al obtener los datos:" ,e)
        return []
    finally:
        conexion.close()
        
    return estadisticas

def obtener_ppp_finalizadas(): 
    conexion = obtener_conexion()
    if not conexion: 
        return {"error": "No se pudo establecer conexion con la base de datos."}
    
    estado_ppp = []
    try:
        with conexion.cursor() as cursor: 
            cursor.execute(
                """
                SELECT
                    COUNT(fechaFin) as total_con_fecha, 
                    COUNT(*) - COUNT(fechaFin) AS total_sin_fecha
                FROM 
                    practicas_preprofesionales;
                """
            )
            #obtener los resultados
            resultado = cursor.fetchone()
            
            # asignar los resultados a un diccionario simple
            estado_ppp = {
                "total_con_fecha": resultado[0], 
                "total_sin_fecha": resultado[1]
            }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
        
    return estado_ppp
