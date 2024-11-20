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

def obtener_practica_por_id(id_practica):
    conexion = obtener_conexion()
    if not conexion:
        return None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.fechaInicio, p.fechaFin, p.horario, p.modalidad, p.area,
                    p.numeroHorasPPP, p.numeroHorasPendientes, p.numeroHorasRealizadas,
                    p.idSemestre, p.idLinea, p.numDocInstitucion, p.idTipoPractica,
                    e.apellidos, e.nombre, p.idPersona, p.idPractica, p.idEstado, p.estadoVigencia, p.semestreFinal
                FROM practicas_preprofesionales p
                JOIN persona e ON p.idPersona = e.idPersona
                WHERE p.idPractica = %s
            """, (id_practica,))
            practica = cursor.fetchone()
            if practica:
                return {
                    "fechaInicio": practica[0],
                    "fechaFin": practica[1],
                    "horario": practica[2],
                    "modalidad": practica[3],
                    "area": practica[4],
                    "numeroHorasPPP": practica[5],
                    "numeroHorasPendientes": practica[6],
                    "numeroHorasRealizadas": practica[7],
                    "idSemestre": practica[8],
                    "idLinea": practica[9],
                    "numDocInstitucion": practica[10],
                    "idTipoPractica": practica[11],
                    "apellidosEstudiante": practica[12],
                    "nombreEstudiante": practica[13],
                    "idPersona": practica[14],
                    "idPractica": practica[15],
                    "idEstado": practica[16],
                    "estadoVigencia": practica[17],
                    "semestreFinal": practica[18]
                }
    except Exception as e:
        print(f"Error al obtener práctica: {str(e)}")
        return None
    finally:
        conexion.close()

def obtener_practica_por_estudiante(id_estudiante):
    conexion = obtener_conexion()
    if not conexion:
        return None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    p.fechaInicio, p.fechaFin, p.horario, p.modalidad, p.area,
                    p.numeroHorasPPP, p.numeroHorasPendientes, p.numeroHorasRealizadas,
                    p.idSemestre, p.idLinea, p.numDocInstitucion, p.idTipoPractica,
                    e.apellidos, e.nombre, p.idPersona, p.idPractica, p.idEstado, p.estadoVigencia, p.semestreFinal
                FROM practicas_preprofesionales p
                JOIN persona e ON p.idPersona = e.idPersona
                WHERE p.idPersona = %s
                  AND p.estadoVigencia = 'P'
                ORDER BY p.fechaInicio DESC
                LIMIT 1
            """, (id_estudiante,))
            
            practica = cursor.fetchone()
            if practica:
                return {
                    "fechaInicio": practica[0],
                    "fechaFin": practica[1],
                    "horario": practica[2],
                    "modalidad": practica[3],
                    "area": practica[4],
                    "numeroHorasPPP": practica[5],
                    "numeroHorasPendientes": practica[6],
                    "numeroHorasRealizadas": practica[7],
                    "idSemestre": practica[8],
                    "idLinea": practica[9],
                    "numDocInstitucion": practica[10],
                    "idTipoPractica": practica[11],
                    "apellidosEstudiante": practica[12],
                    "nombreEstudiante": practica[13],
                    "idPersona": practica[14],
                    "idPractica": practica[15],
                    "idEstado": practica[16],
                    "estadoVigencia": practica[17],
                    "semestreFinal": practica[18]
                }
            else:
                return {"mensaje": "No se encontró una práctica activa para este estudiante."}
    except Exception as e:
        print(f"Error al obtener la práctica del estudiante: {str(e)}")
        return {"error": str(e)}
    finally:
        conexion.close()

def informes_practica(idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute(""" 
                SELECT 
                    p.idPractica,
                    EXISTS (
                        SELECT 1 
                        FROM informes_practicas_preprofesionales dipp
                        JOIN informe i ON dipp.IidInforme = i.idInforme
                        WHERE dipp.idPractica = p.idPractica 
                        AND i.idTipoInforme = 1 
                        AND i.estado = 'A'
                    ) AS informe1,
                    EXISTS (
                        SELECT 1 
                        FROM informes_practicas_preprofesionales dipp
                        JOIN informe i ON dipp.IidInforme = i.idInforme
                        WHERE dipp.idPractica = p.idPractica 
                        AND i.idTipoInforme = 2 
                        AND i.estado = 'A'
                    ) AS informe2,
                    EXISTS (
                        SELECT 1 
                        FROM informes_practicas_preprofesionales dipp
                        JOIN informe i ON dipp.IidInforme = i.idInforme
                        WHERE dipp.idPractica = p.idPractica 
                        AND i.idTipoInforme = 3 
                        AND i.estado = 'A'
                    ) AS informe3,
                    EXISTS (
                        SELECT 1 
                        FROM informes_practicas_preprofesionales dipp
                        JOIN informe i ON dipp.IidInforme = i.idInforme
                        WHERE dipp.idPractica = p.idPractica 
                        AND i.idTipoInforme = 4 
                        AND i.estado = 'A'
                    ) AS informe4
                FROM 
                    practicas_preprofesionales p
                WHERE 
                    p.idPractica = %s
            """, (idPractica,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                informes_dict = dict(zip(columnas, row))
                return informes_dict
            else:
                return {"error": "Práctica no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_practica(idPractica, fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas, idSemestre, idLinea, numDocInstitucion, idTipoPractica, idPersona):
    # Validaciones
    if not fechaInicio or not horario or not modalidad or not area or not numeroHorasPPP or not numeroHorasPendientes or not numeroHorasRealizadas or not idSemestre or not idLinea or not numDocInstitucion or not idTipoPractica or not idPersona:
        return {"error": "Todos los campos son requeridos."}

    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Verificar si el idPractica ya existe
            cursor.execute("SELECT idPractica FROM practicas_preprofesionales WHERE idPractica = %s", (idPractica,))
            practica_existente = cursor.fetchone()

            if practica_existente:
                # Actualizar los campos permitidos
                cursor.execute("""
                    UPDATE practicas_preprofesionales
                    SET horario = %s, modalidad = %s, area = %s,
                        numeroHorasPPP = %s, numeroHorasPendientes = %s, numeroHorasRealizadas = %s,
                        idLinea = %s, numDocInstitucion = %s, idTipoPractica = %s, estadoVigencia = %s, idEstado = %s
                    WHERE idPractica = %s
                """, (horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas,
                      idLinea, numDocInstitucion, idTipoPractica, 'P', 1, idPractica))
                conexion.commit()
                return {"mensaje": "Práctica actualizada correctamente"}
            else:
                # Insertar nueva práctica
                cursor.execute("""
                    INSERT INTO practicas_preprofesionales (idPractica, fechaInicio, horario, modalidad, area,
                                                            numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas,
                                                            estadoVigencia, idSemestre, idLinea, numDocInstitucion, idEstado,
                                                            idTipoPractica, idPersona)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (idPractica, fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes,
                      numeroHorasRealizadas, 'P', idSemestre, idLinea, numDocInstitucion, 1, idTipoPractica, idPersona))
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

def obtener_reporte_horas_practicas2(codUniversitario=None):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    reporte_horas = []
    try:
        with conexion.cursor() as cursor:
            # Agregar el filtro en la consulta SQL usando el parámetro codUniversitario
            consulta = """
            SELECT 
                p.nombre AS Nombre_Alumno,
                p.apellidos AS Apellidos_Alumno,
                p.codUniversitario AS Codigo_Universitario,
                e.nombre AS Escuela,
                sa.nombre AS Semestre_Academico,
                i.razonSocial AS Institucion,
                tp.nombre AS Tipo_Practica,
                ppp.modalidad AS Modalidad,
                ppp.area AS Area,
                ppp.fechaInicio AS Fecha_Inicio,
                ppp.fechaFin AS Fecha_Fin,
                ppp.numeroHorasPPP AS Horas_Requeridas,
                ppp.numeroHorasRealizadas AS Horas_Completadas,
                ppp.numeroHorasPendientes AS Horas_Pendientes,
                ROUND((ppp.numeroHorasRealizadas / ppp.numeroHorasPPP) * 100, 2) AS Porcentaje_Avance,
                es.nombre AS Estado_Practica
            FROM 
                persona p
                INNER JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
                INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                INNER JOIN semestre_academico sa ON ppp.idSemestre = sa.idSemestre
                INNER JOIN institucion i ON ppp.numDocInstitucion = i.numDoc
                INNER JOIN tipo_practicas tp ON ppp.idTipoPractica = tp.idTipoPractica
                INNER JOIN estado es ON ppp.idEstado = es.idEstado
            WHERE 
                p.estado = 'A'
            """
            # Si se proporciona codUniversitario, añadir la condición de filtro
            if codUniversitario:
                consulta += " AND p.codUniversitario = %s"
            
            consulta += " ORDER BY p.apellidos, p.nombre, sa.nombre;"
            
            # Ejecutar la consulta con o sin parámetro según corresponda
            if codUniversitario:
                cursor.execute(consulta, (codUniversitario,))
            else:
                cursor.execute(consulta)
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            print("Filas obtenidas:", len(rows)) 

            for row in rows:
                reporte_dict = dict(zip(column_names, row))
                # Agregar información adicional sobre el estado de las horas
                reporte_dict['Estado_Horas'] = 'Completado' if reporte_dict['Horas_Pendientes'] == 0 else 'En Proceso'
                # Formatear modalidad
                reporte_dict['Modalidad'] = 'Presencial' if reporte_dict['Modalidad'] == 'P' else 'Virtual' if reporte_dict['Modalidad'] == 'V' else 'Híbrido'
                reporte_horas.append(reporte_dict)

    except Exception as e:
        return {"error": f"Error al generar el reporte: {str(e)}"}
    finally:
        conexion.close()
    
    return reporte_horas
