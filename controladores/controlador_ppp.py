from bd import obtener_conexion

# OPERACIONES CRUD

def obtener_practicas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas = []
    try:
        with conexion.cursor() as cursor:
            # Ajusta la consulta para obtener el idPractica y el nombre completo del estudiante por separado
            query = """
                SELECT 
                    p.idPractica,
                    CONCAT(e.nombre, ' ', e.apellidos) AS estudiante, 
                    p.fechaInicio,
                    p.fechaFin,
                    CASE 
                        WHEN p.modalidad = 'P' THEN 'Presencial'
                        WHEN p.modalidad = 'V' THEN 'Virtual'
                        WHEN p.modalidad = 'M' THEN 'Mixta'
                    END AS modalidad,
                    p.area,
                    p.numeroHorasPPP,
                    p.numeroHorasRealizadas
                FROM practicas_preprofesionales p
                JOIN estudiante e ON p.numDocEstudiante = e.numDoc
            """
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas.append(practica_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return practicas

def obtener_practica_por_id(idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practica = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM practicas_preprofesionales WHERE idPractica = %s", (idPractica,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                practica_dict = dict(zip(columnas, row))
                return practica_dict
            else:
                return {"error": "Práctica no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_practica(fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas, idSemestre, idLinea, numDocInstitucion, idTipoPractica, idPersona):
    # Validaciones
    if not fechaInicio or not horario or not modalidad or not area or not numeroHorasPPP or not numeroHorasPendientes or not numeroHorasRealizadas or not idSemestre or not idLinea or not numDocInstitucion or not idTipoPractica or not idPersona:
        return {"error": "Todos los campos son requeridos."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Insertar la práctica preprofesional
            cursor.execute("""
                INSERT INTO practicas_preprofesionales (fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas, estadoVigencia, idSemestre, idLinea, numDocInstitucion, idEstado, idTipoPractica, idPersona)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            """, (fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas, 'P', idSemestre, idLinea, numDocInstitucion, 1, idTipoPractica, idPersona))
            conexion.commit()
            return {"mensaje": "Práctica agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_practica(idPractica, fechaInicio, fechaFin, modalidad, area, numeroHorasPPP, numDocEstudiante, idSemestre, idLinea, numDocInstitucion, idEstado, idTipoPractica):
    # Validaciones
    if not idPractica or not fechaInicio or not fechaFin or not modalidad or not area or not numeroHorasPPP or not numDocEstudiante or not idSemestre or not idLinea or not numDocInstitucion or not idEstado or not idTipoPractica:
        return {"error": "Todos los campos son requeridos."}

    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Modificar la práctica preprofesional
            cursor.execute("""
                UPDATE practicas_preprofesionales
                SET fechaInicio = %s, fechaFin = %s, modalidad = %s, area = %s, numeroHorasPPP = %s, numDocEstudiante = %s, idSemestre = %s, idLinea = %s, numDocInstitucion = %s, idEstado = %s, idTipoPractica = %s
                WHERE idPractica = %s
            """, (fechaInicio, fechaFin, modalidad, area, numeroHorasPPP, numDocEstudiante, idSemestre, idLinea, numDocInstitucion, idEstado, idTipoPractica, idPractica))
            conexion.commit()
            return {"mensaje": "Práctica modificada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_practica(idPractica):
    # Validaciones
    if not idPractica:
        return {"error": "El ID de la práctica es requerido."}

    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Eliminar la práctica preprofesional
            cursor.execute("DELETE FROM practicas_preprofesionales WHERE idPractica = %s", (idPractica,))
            conexion.commit()
            return {"mensaje": "Práctica eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def cambiar_estado_practica(idPractica, nuevo_estado):
    # Validaciones
    if not idPractica or not nuevo_estado:
        return {"error": "El ID de la práctica y el nuevo estado son requeridos."}
    if nuevo_estado not in ['A', 'I']:
        return {"error": "El estado debe ser 'A' (Activo) o 'I' (Inactivo)."}

    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Cambiar el estado de la práctica
            cursor.execute("""
                UPDATE practicas_preprofesionales
                SET idEstado = %s
                WHERE idPractica = %s
            """, (nuevo_estado, idPractica))
            conexion.commit()
            return {"mensaje": "Estado de la práctica actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

# OTRAS OPERACIONES

def obtener_practicas_activas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS practicas_activas FROM practicas_preprofesionales WHERE idEstado = 'A'")
            row = cursor.fetchone()

            if row:
                return {"practicas_activas": row[0]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_practicas_con_estado():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    idPractica, 
                    area, 
                    CASE 
                        WHEN idEstado = 'A' THEN 'Activo' 
                        ELSE 'Inactivo' 
                    END AS estado 
                FROM practicas_preprofesionales 
                ORDER BY area
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas.append(practica_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

    return practicas

def obtener_ultimo_id():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas = []
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT COALESCE(MAX(idPractica), 0) + 1 AS ultimoID
                FROM practicas_preprofesionales;
            """
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas.append(practica_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return practicas

############################# REPORTES ESTUDIANTES PRÁCTICAS #############################
def reporte_practicas_estudiantes(idSemestre, idEscuela, idEstado, numDoc): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    practicas_estudiante = []
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT 
                    pe.codUniversitario, 
                    pe.apellidos, 
                    pe.nombre, 
                    pe.tel1, 
                    pe.correoUSAT
                FROM persona AS pe
                INNER JOIN practicas_preprofesionales pp ON pe.idPersona = pp.idPersona
                INNER JOIN estado est ON pp.idEstado = est.idEstado
                INNER JOIN semestre_academico sem ON pp.idSemestre = sem.idSemestre
                INNER JOIN escuela esc ON esc.idEscuela = pe.idEscuela
                INNER JOIN institucion ins ON ins.numDoc = pp.numDocInstitucion
                WHERE 
                    (sem.idSemestre = %s OR %s = 0) AND
                    (esc.idEscuela = %s OR %s = 0) AND
                    (est.idEstado = %s OR %s = 0) AND
                    (ins.numDoc = %s OR %s = 0)
                GROUP BY pe.idPersona
            """
            cursor.execute(query, (idSemestre, idSemestre, idEscuela, idEscuela, idEstado, idEstado, numDoc, numDoc))
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas_estudiante.append(practica_dict)
                
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

    return {"data": practicas_estudiante}
