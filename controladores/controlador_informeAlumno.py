from bd import obtener_conexion
from datetime import datetime

def obtener_informeAlumno():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    informesAlumnos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT 
                p.nombre AS Nombre_Alumno,
                p.apellidos AS Apellidos_Alumno,
                sa.nombre AS Semestre_Academico,
                ppp.idPractica AS ID_Practica,
                -- Informe inicial (tipo 1)
                EXISTS(
                    SELECT 1 
                    FROM informes_practicas_preprofesionales ippp 
                    JOIN informe i ON ippp.IidInforme = i.idInforme
                    WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 1
                ) AS Informe_Inicial_Existe,
                (SELECT i.idInforme 
                FROM informes_practicas_preprofesionales ippp 
                JOIN informe i ON ippp.IidInforme = i.idInforme
                WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 1
                LIMIT 1) AS Informe_Inicial_ID,
                -- Informe final (tipo 2)
                EXISTS(
                    SELECT 1 
                    FROM informes_practicas_preprofesionales ippp 
                    JOIN informe i ON ippp.IidInforme = i.idInforme
                    WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 2
                ) AS Informe_Final_Existe,
                (SELECT i.idInforme 
                FROM informes_practicas_preprofesionales ippp 
                JOIN informe i ON ippp.IidInforme = i.idInforme
                WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 2
                LIMIT 1) AS Informe_Final_ID,
                -- Informe de tipo 3
                EXISTS(
                    SELECT 1 
                    FROM informes_practicas_preprofesionales ippp 
                    JOIN informe i ON ippp.IidInforme = i.idInforme
                    WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 3
                ) AS Informe_Tipo3_Existe,
                (SELECT i.idInforme 
                FROM informes_practicas_preprofesionales ippp 
                JOIN informe i ON ippp.IidInforme = i.idInforme
                WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 3
                LIMIT 1) AS Informe_Tipo3_ID,
                -- Informe de tipo 4
                EXISTS(
                    SELECT 1 
                    FROM informes_practicas_preprofesionales ippp 
                    JOIN informe i ON ippp.IidInforme = i.idInforme
                    WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 4
                ) AS Informe_Tipo4_Existe,
                (SELECT i.idInforme 
                FROM informes_practicas_preprofesionales ippp 
                JOIN informe i ON ippp.IidInforme = i.idInforme
                WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 4
                LIMIT 1) AS Informe_Tipo4_ID,
                -- Informe de tipo 5 (en la tabla ficha_evaluacion)
                EXISTS(
                    SELECT 1 
                    FROM ficha_evaluacion fe
                    WHERE fe.idPractica = ppp.idPractica AND fe.idTipoInforme = 5
                ) AS Informe_Tipo5_Existe,
                (SELECT fe.idFichaEvaluacion 
                FROM ficha_evaluacion fe
                WHERE fe.idPractica = ppp.idPractica AND fe.idTipoInforme = 5
                LIMIT 1) AS Informe_Tipo5_ID,
                -- Informe de tipo 6
                EXISTS(
                    SELECT 1 
                    FROM informes_practicas_preprofesionales ippp 
                    JOIN informe i ON ippp.IidInforme = i.idInforme
                    WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 6
                ) AS Informe_Tipo6_Existe,
                (SELECT i.idInforme 
                FROM informes_practicas_preprofesionales ippp 
                JOIN informe i ON ippp.IidInforme = i.idInforme
                WHERE ippp.idPractica = ppp.idPractica AND i.idTipoInforme = 6
                LIMIT 1) AS Informe_Tipo6_ID
            FROM 
                persona p
            JOIN 
                usuario u ON p.idUsuario = u.idUsuario
            JOIN 
                practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
            JOIN 
                semestre_academico sa ON ppp.idSemestre = sa.idSemestre
            WHERE 
                u.idTipoUsuario = 3 -- Solo estudiantes
            ORDER BY 
                p.apellidos, p.nombre;
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                informesAlumnos_dict = dict(zip(column_names, row))
                informesAlumnos.append(informesAlumnos_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return informesAlumnos


# reporte 4
def obtener_reporte_horas_practicas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    reporte_horas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
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
            ORDER BY 
                p.apellidos, p.nombre, sa.nombre;
            """)
            
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


# reporte 5
def obtener_resumen_horas_por_escuela():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    resumen_escuelas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT 
                e.nombre AS Escuela,
                COUNT(DISTINCT p.idPersona) AS Total_Estudiantes,
                SUM(ppp.numeroHorasRealizadas) AS Total_Horas_Realizadas,
                SUM(ppp.numeroHorasPendientes) AS Total_Horas_Pendientes,
                ROUND(AVG((ppp.numeroHorasRealizadas / ppp.numeroHorasPPP) * 100), 2) AS Promedio_Avance
            FROM 
                escuela e
                INNER JOIN persona p ON e.idEscuela = p.idEscuela
                INNER JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
            WHERE 
                p.estado = 'A'  -- Cambiado de '1' a 'A'
            GROUP BY 
                e.nombre
            ORDER BY 
                e.nombre;
            """)
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                resumen_dict = dict(zip(column_names, row))
                resumen_escuelas.append(resumen_dict)

    except Exception as e:
        return {"error": f"Error al generar el resumen por escuela: {str(e)}"}
    finally:
        conexion.close()
    
    return resumen_escuelas


def obtener_practicas_terminadas_mes(mes=None, anio=None):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas_terminadas = []
    try:
        with conexion.cursor() as cursor:
            if not mes or not anio:
                from datetime import datetime
                fecha_actual = datetime.now()
                mes = fecha_actual.month
                anio = fecha_actual.year

            cursor.execute("""
            SELECT 
                p.nombre AS Nombre_Alumno,
                p.apellidos AS Apellidos_Alumno,
                p.codUniversitario AS Codigo_Universitario,
                e.nombre AS Escuela,
                sa.nombre AS Semestre_Academico,
                i.razonSocial AS Institucion,
                ppp.fechaInicio AS Fecha_Inicio,
                ppp.fechaFin AS Fecha_Fin,
                ppp.numeroHorasPPP AS Horas_Requeridas,
                ppp.numeroHorasRealizadas AS Horas_Completadas,
                est.nombre AS Estado_Practica
            FROM 
                practicas_preprofesionales ppp
                INNER JOIN persona p ON p.idPersona = ppp.idPersona
                INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                INNER JOIN semestre_academico sa ON ppp.idSemestre = sa.idSemestre
                INNER JOIN institucion i ON ppp.numDocInstitucion = i.numDoc
                INNER JOIN estado est ON ppp.idEstado = est.idEstado
            WHERE 
                p.estado = 'A'
                AND MONTH(ppp.fechaFin) = %s
                AND YEAR(ppp.fechaFin) = %s
                AND ppp.numeroHorasRealizadas >= ppp.numeroHorasPPP
                AND ppp.estadoVigencia = 'P'
            ORDER BY 
                ppp.fechaFin DESC;
            """, (mes, anio))
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas_terminadas.append(practica_dict)

    except Exception as e:
        return {"error": f"Error al generar el reporte: {str(e)}"}
    finally:
        conexion.close()
    
    return practicas_terminadas


def obtener_dashboard_tendencias_escuela():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        resultados = {
            "tendencias_generales": [],
            "modalidades_por_escuela": [],
            "instituciones_populares": [],
            "tasas_finalizacion": []
        }
        
        with conexion.cursor() as cursor:
            # 1. Tendencias generales por escuela - Ajustada la condición de finalizadas
            cursor.execute("""
            SELECT 
                e.nombre AS Escuela,
                COUNT(ppp.idPractica) AS Total_Practicas,
                ROUND(COALESCE(AVG(NULLIF(ppp.numeroHorasRealizadas, 0)), 0), 2) AS Promedio_Horas,
                COUNT(CASE WHEN ppp.idEstado = 4 THEN 1 END) AS Practicas_Finalizadas,
                COUNT(CASE WHEN ppp.estadoVigencia = 'P' THEN 1 END) AS Practicas_Vigentes
            FROM 
                escuela e
                LEFT JOIN persona p ON e.idEscuela = p.idEscuela
                LEFT JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
            WHERE 
                p.estado = 'A'
                AND ppp.idPractica IS NOT NULL
                AND ppp.estadoVigencia = 'P'
            GROUP BY 
                e.nombre
            ORDER BY 
                Total_Practicas DESC
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            resultados["tendencias_generales"] = [dict(zip(column_names, row)) for row in rows]

            # 2. Modalidades por escuela
            cursor.execute("""
            SELECT 
                e.nombre AS Escuela,
                ppp.modalidad,
                COUNT(*) AS Total,
                ROUND(AVG(ppp.numeroHorasRealizadas), 2) AS Promedio_Horas
            FROM 
                escuela e
                JOIN persona p ON e.idEscuela = p.idEscuela
                JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
            WHERE 
                p.estado = 'A'
                AND ppp.estadoVigencia = 'P'
            GROUP BY 
                e.nombre, ppp.modalidad
            ORDER BY 
                e.nombre, Total DESC
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            resultados["modalidades_por_escuela"] = [dict(zip(column_names, row)) for row in rows]

            # 3. Top instituciones por escuela
            cursor.execute("""
            SELECT 
                e.nombre AS Escuela,
                i.razonSocial AS Institucion,
                COUNT(*) AS Total_Practicantes,
                ROUND(AVG(ppp.numeroHorasRealizadas), 2) AS Promedio_Horas
            FROM 
                escuela e
                JOIN persona p ON e.idEscuela = p.idEscuela
                JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
                JOIN institucion i ON ppp.numDocInstitucion = i.numDoc
            WHERE 
                p.estado = 'A'
                AND ppp.estadoVigencia = 'P'
            GROUP BY 
                e.nombre, i.razonSocial
            HAVING 
                Total_Practicantes >= 1
            ORDER BY 
                e.nombre, Total_Practicantes DESC
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            resultados["instituciones_populares"] = [dict(zip(column_names, row)) for row in rows]

            # 4. Tasas de finalización por mes
            cursor.execute("""
SELECT 
    e.nombre AS Escuela,
    YEAR(ppp.fechaFin) AS Anio,
    MONTH(ppp.fechaFin) AS Mes,
    COUNT(DISTINCT ppp.idPractica) AS Total_Practicas,
    COUNT(DISTINCT CASE WHEN ppp.idEstado = 4 THEN ppp.idPractica END) AS Completadas,
    ROUND(
        (COUNT(DISTINCT CASE WHEN ppp.idEstado = 4 THEN ppp.idPractica END) * 100.0) / 
        NULLIF(COUNT(DISTINCT ppp.idPractica), 0), 
        2
    ) AS Tasa_Finalizacion
FROM 
    escuela e
    JOIN persona p ON e.idEscuela = p.idEscuela
    JOIN practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
WHERE 
    p.estado = 'A'
    AND ppp.estadoVigencia = 'P'
    AND YEAR(ppp.fechaFin) = YEAR(CURRENT_DATE)
    AND ppp.fechaFin IS NOT NULL
GROUP BY 
    e.nombre, YEAR(ppp.fechaFin), MONTH(ppp.fechaFin)
HAVING 
    Total_Practicas > 0
ORDER BY 
    e.nombre, Mes ASC
""")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            resultados["tasas_finalizacion"] = [dict(zip(column_names, row)) for row in rows]

        return resultados

    except Exception as e:
        return {"error": f"Error al generar el dashboard: {str(e)}"}
    finally:
        conexion.close()
        
        
        

def obtener_semestres():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT DISTINCT 
                sa.idSemestre,
                sa.nombre AS Semestre
            FROM 
                semestre_academico sa
            ORDER BY 
                sa.nombre DESC
            """)
            
            semestres = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
            return semestres

    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_practicas_terminadas_semestre(id_semestre):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas_terminadas = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT 
                p.apellidos AS Apellidos_Alumno,
                p.nombre AS Nombre_Alumno,
                p.codUniversitario AS Codigo_Universitario,
                e.nombre AS Escuela,
                sa.nombre AS Semestre_Academico,
                i.razonSocial AS Institucion,
                ppp.fechaInicio AS Fecha_Inicio,
                ppp.fechaFin AS Fecha_Fin,
                ppp.numeroHorasPPP AS Horas_Requeridas,
                ppp.numeroHorasRealizadas AS Horas_Completadas,
                est.nombre AS Estado_Practica
            FROM 
                practicas_preprofesionales ppp
                INNER JOIN persona p ON p.idPersona = ppp.idPersona
                INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                INNER JOIN semestre_academico sa ON ppp.idSemestre = sa.idSemestre
                INNER JOIN institucion i ON ppp.numDocInstitucion = i.numDoc
                INNER JOIN estado est ON ppp.idEstado = est.idEstado
            WHERE 
                p.estado = 'A'
                AND ppp.idSemestre = %s
                AND ppp.numeroHorasRealizadas >= ppp.numeroHorasPPP
                AND ppp.estadoVigencia = 'P'
            ORDER BY 
                p.apellidos, p.nombre;
            """, (id_semestre,))
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas_terminadas.append(practica_dict)

    except Exception as e:
        return {"error": f"Error al generar el reporte: {str(e)}"}
    finally:
        conexion.close()
    
    return practicas_terminadas      


def obtener_escuelas():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT DISTINCT 
                e.idEscuela,
                e.nombre AS Escuela
            FROM 
                escuela e
            ORDER BY 
                e.nombre
            """)
            
            escuelas = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]
            return escuelas

    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_instituciones_por_escuela(id_escuela):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
            SELECT 
                i.razonSocial AS Institucion,
                COUNT(*) AS Total_Practicantes
            FROM 
                institucion i
                JOIN practicas_preprofesionales ppp ON i.numDoc = ppp.numDocInstitucion
                JOIN persona p ON ppp.idPersona = p.idPersona
            WHERE 
                p.idEscuela = %s
                AND p.estado = 'A'
                AND ppp.estadoVigencia = 'P'
            GROUP BY 
                i.razonSocial
            ORDER BY 
                Total_Practicantes DESC
            """, (id_escuela,))
            
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            instituciones = [dict(zip(column_names, row)) for row in rows]
            return instituciones

    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close() 

# Controlador para obtener detalles de un informe
def obtener_detalle_informe(idInforme):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    try:
        with conexion.cursor() as cursor:
            # Intentar obtener el informe de la tabla 'informe'
            cursor.execute("""
                SELECT 
                    idInforme AS ID_Informe,
                    fecha AS Fecha,
                    estado AS Estado,
                    idTipoInforme AS TipoInforme
                FROM informe
                WHERE idInforme = %s
            """, (idInforme,))
            resultado = cursor.fetchone()
            
            if resultado:
                # Mapear el estado del informe
                estado_map = {
                    "A": "Aprobado",
                    "P": "Pendiente de aprobación",
                    "R": "Rechazado"
                }
                
                # Mapeamos los resultados a un diccionario
                detalle_informe = {
                    "idInforme": resultado[0],
                    "fecha": resultado[1],
                    "estado": estado_map.get(resultado[2], "Estado desconocido"),
                    "tipoInforme": resultado[3]
                }
                return detalle_informe
            else:
                # Si no se encuentra en la tabla 'informe', buscar en 'ficha_evaluacion'
                cursor.execute("""
                    SELECT 
                        idFichaEvaluacion AS ID_Informe,
                        fecha_evaluacion AS Fecha,
                        estado AS Estado,
                        idTipoInforme AS TipoInforme
                    FROM ficha_evaluacion
                    WHERE idFichaEvaluacion = %s
                """, (idInforme,))
                resultado_ficha = cursor.fetchone()
                
                if resultado_ficha:
                    # Mapear el estado del informe
                    estado_map = {
                        "A": "Aprobado",
                        "P": "Pendiente de aprobación",
                        "R": "Rechazado"
                    }
                    
                    # Mapeamos los resultados a un diccionario
                    detalle_informe = {
                        "idInforme": resultado_ficha[0],
                        "fecha": resultado_ficha[1],
                        "estado": estado_map.get(resultado_ficha[2], "Estado desconocido"),
                        "tipoInforme": resultado_ficha[3]
                    }
                    return detalle_informe
                else:
                    # Si no se encuentra en ambas tablas
                    return {"error": "No se encontró ningún informe con el ID proporcionado."}
    except Exception as e:
        return {"error": f"Error al obtener el detalle del informe: {str(e)}"}
    finally:
        conexion.close()

# Controlador para aprobar un informe
def aprobar_informe(idInforme):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Verificar el estado del informe en la tabla 'informe'
            cursor.execute("""
                SELECT estado
                FROM informe
                WHERE idInforme = %s
            """, (idInforme,))
            resultado = cursor.fetchone()

            if not resultado:
                # Si no se encuentra en 'informe', buscar en 'ficha_evaluacion'
                cursor.execute("""
                    SELECT estado
                    FROM ficha_evaluacion
                    WHERE idFichaEvaluacion = %s
                """, (idInforme,))
                resultado_ficha = cursor.fetchone()

                if not resultado_ficha:
                    return {"error": "El informe no existe."}

                # Si se encuentra en 'ficha_evaluacion', actualizar su estado
                estado_actual_ficha = resultado_ficha[0]
                if estado_actual_ficha == 'A':
                    return {"error": "El informe ya está aprobado."}

                # Actualizar el estado del informe en 'ficha_evaluacion'
                cursor.execute("""
                    UPDATE ficha_evaluacion
                    SET estado = 'A'
                    WHERE idFichaEvaluacion = %s
                """, (idInforme,))
                
            else:
                # Si se encuentra en 'informe', verificar y actualizar su estado
                estado_actual = resultado[0]
                if estado_actual == 'A':
                    return {"error": "El informe ya está aprobado."}

                # Actualizar el estado del informe a 'A' (Aprobado)
                cursor.execute("""
                    UPDATE informe
                    SET estado = 'A'
                    WHERE idInforme = %s
                """, (idInforme,))

            # Confirmar los cambios
            conexion.commit()
            
            return {"mensaje": "El informe fue aprobado correctamente."}
    except Exception as e:
        conexion.rollback()  # Revertir los cambios en caso de error
        return {"error": f"Error al aprobar el informe: {str(e)}"}
    finally:
        conexion.close()


# Controlador para rechazar un informe
def rechazar_informe(idInforme):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            # Verificar el estado del informe en la tabla 'informe'
            cursor.execute("""
                SELECT estado
                FROM informe
                WHERE idInforme = %s
            """, (idInforme,))
            resultado = cursor.fetchone()

            if not resultado:
                # Si no se encuentra en 'informe', buscar en 'ficha_evaluacion'
                cursor.execute("""
                    SELECT estado
                    FROM ficha_evaluacion
                    WHERE idFichaEvaluacion = %s
                """, (idInforme,))
                resultado_ficha = cursor.fetchone()

                if not resultado_ficha:
                    return {"error": "El informe no existe."}

                # Si se encuentra en 'ficha_evaluacion', verificar y actualizar su estado
                estado_actual_ficha = resultado_ficha[0]
                if estado_actual_ficha == 'R':
                    return {"error": "El informe ya está rechazado."}

                # Actualizar el estado del informe en 'ficha_evaluacion'
                cursor.execute("""
                    UPDATE ficha_evaluacion
                    SET estado = 'R'
                    WHERE idFichaEvaluacion = %s
                """, (idInforme,))
                
            else:
                # Si se encuentra en 'informe', verificar y actualizar su estado
                estado_actual = resultado[0]
                if estado_actual == 'R':
                    return {"error": "El informe ya está rechazado."}

                # Actualizar el estado del informe a 'R' (Rechazado)
                cursor.execute("""
                    UPDATE informe
                    SET estado = 'R'
                    WHERE idInforme = %s
                """, (idInforme,))

            # Confirmar los cambios
            conexion.commit()
            
            return {"mensaje": "El informe fue rechazado correctamente."}
    except Exception as e:
        conexion.rollback()  # Revertir los cambios en caso de error
        return {"error": f"Error al rechazar el informe: {str(e)}"}
    finally:
        conexion.close()


