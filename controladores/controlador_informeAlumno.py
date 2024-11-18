from bd import obtener_conexion
from datetime import datetime

# Obtener todas las escuelas
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
                IFNULL(ii.idInforme, 'Por subir') AS Informe_Inicial,
                IFNULL(ifin.idInforme, 'Por subir') AS Informe_Final
            FROM 
                persona p
            JOIN 
                usuario u ON p.idUsuario = u.idUsuario
            JOIN 
                practicas_preprofesionales ppp ON p.idPersona = ppp.idPersona
            JOIN 
                semestre_academico sa ON ppp.idSemestre = sa.idSemestre
            LEFT JOIN 
                informes_practicas_preprofesionales ippp_i ON ppp.idPractica = ippp_i.idPractica
            LEFT JOIN 
                informe ii ON ippp_i.IidInforme = ii.idInforme AND ii.idTipoInforme = 1 -- Informe inicial
            LEFT JOIN 
                informes_practicas_preprofesionales ippp_f ON ppp.idPractica = ippp_f.idPractica
            LEFT JOIN 
                informe ifin ON ippp_f.IidInforme = ifin.idInforme AND ifin.idTipoInforme = 2 -- Informe final
            WHERE 
                u.idTipoUsuario = 3;
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