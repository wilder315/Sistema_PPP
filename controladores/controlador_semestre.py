from bd import obtener_conexion

def obtener_semestres():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    semestres = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM semestre_academico ORDER BY nombre DESC")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                semestre_dict = dict(zip(column_names, row))
                if 'fechaInicio' in semestre_dict and semestre_dict['fechaInicio']:
                    semestre_dict['fechaInicio'] = semestre_dict['fechaInicio'].strftime('%d/%m/%Y')
                if 'fechaFin' in semestre_dict and semestre_dict['fechaFin']:
                    semestre_dict['fechaFin'] = semestre_dict['fechaFin'].strftime('%d/%m/%Y')
                
                semestres.append(semestre_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return semestres

def obtener_semestre_por_id(idSemestre):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}    
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM semestre_academico WHERE idSemestre = %s", (idSemestre,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                semestre_dict = dict(zip(columnas, row))
                return semestre_dict
            else:
                return {"error": "Semestre no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_semestre(nombre, fechaInicio, fechaFin, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO semestre_academico (nombre, fechaInicio, fechaFin, estado) 
                VALUES (%s, %s, %s, %s)
            """, (nombre, fechaInicio, fechaFin, estado))
            conexion.commit()
            return {"mensaje": "Semestre agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_semestre(idSemestre, nombre, fechaInicio, fechaFin, estado):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE semestre_academico 
                SET nombre = %s, fechaInicio = %s, fechaFin = %s, estado = %s 
                WHERE idSemestre = %s
            """, (nombre, fechaInicio, fechaFin, estado, idSemestre))
            conexion.commit()
            return {"mensaje": "Semestre modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_semestre(idSemestre):
    if not idSemestre:
        return {"error": "El ID del semestre es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM semestre_academico WHERE idSemestre = %s", (idSemestre,))
            conexion.commit()
            return {"mensaje": "Semestre eliminado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_semestre(idSemestre):
    if not idSemestre:
        return {"error": "El ID del semestre es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE semestre_academico SET estado = 'I' WHERE idSemestre = %s", (idSemestre,))
            conexion.commit()
            return {"mensaje": "Semestre dado de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()
        
######################################## código del dashboard 02 #########################

def obtener_datos_dashboard2(idEscuela, idSemestre):
    conexion = obtener_conexion()
    datos = {
        'estudiantes': 0,
        'docentes': 0,
        'instituciones': 0,
        'jefes': 0
    }
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT
                    -- Contar estudiantes
                    (SELECT COUNT(distinct pe.idPersona) 
                    FROM persona pe 
                    INNER JOIN usuario usu ON usu.idUsuario = pe.idUsuario
                    LEFT JOIN practicas_preprofesionales pp ON pp.idPersona = pe.idPersona
                    LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                    WHERE usu.idTipoUsuario = 3 
                    AND (%s = 0 OR li.idEscuela = %s)
                    AND (%s = 0 OR pp.idSemestre = %s)) AS estudiantes,

                    -- Contar docentes
                    (SELECT COUNT(distinct pe.idPersona) 
                    FROM persona pe
                    INNER JOIN usuario usu ON usu.idUsuario = pe.idUsuario
                    LEFT JOIN practicas_preprofesionales pp ON pp.idPersona = pe.idPersona
                    LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                    WHERE usu.idTipoUsuario IN (1, 2) 
                    AND (%s = 0 OR li.idEscuela = %s)
                    AND (%s = 0 OR pp.idSemestre = %s)) AS docentes,

                    -- Contar instituciones
                    (SELECT COUNT(distinct inst.numDoc) 
                    FROM institucion inst 
                    LEFT JOIN practicas_preprofesionales pp ON pp.numDocInstitucion = inst.numDoc
                    LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                    WHERE (%s = 0 OR li.idEscuela = %s)
                    AND (%s = 0 OR pp.idSemestre = %s)) AS instituciones,

                    -- Contar jefes
                    (SELECT COUNT(distinct pe.idPersona) 
                    FROM persona pe
                    INNER JOIN usuario usu ON usu.idUsuario = pe.idUsuario
                    LEFT JOIN practicas_preprofesionales pp ON pp.idPersona = pe.idPersona
                    LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                    WHERE usu.idTipoUsuario = 4
                    AND (%s = 0 OR li.idEscuela = %s)
                    AND (%s = 0 OR pp.idSemestre = %s)) AS jefes;
            """
            cursor.execute(query, (
                idEscuela, idEscuela, idSemestre, idSemestre,  # Estudiantes
                idEscuela, idEscuela, idSemestre, idSemestre, # Docentes
                idEscuela, idEscuela, idSemestre, idSemestre, # Instituciones
                idEscuela, idEscuela, idSemestre, idSemestre #jefes
            ))
            result = cursor.fetchone()

            if result:
                datos['estudiantes'] = result[0]
                datos['docentes'] = result[1]
                datos['instituciones'] = result[2]
                datos['jefes'] = result[3]
    except Exception as e:
        print(f"Error al obtener datos del dashboard: {e}")
    finally:
        conexion.close()
    return datos

def obtener_ultimos_estudiantes(idEscuela, idSemestre): 
    conexion = obtener_conexion()
    estudiantes = []
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT pe.codUniversitario, CONCAT( pe.apellidos, ' ' ,pe.nombre) AS nombres, pe.correoUSAT
                FROM persona pe 
                INNER JOIN usuario usu ON pe.idUsuario = usu.idUsuario
                LEFT JOIN practicas_preprofesionales pp ON pp.idPersona = pe.idPersona
                LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                WHERE usu.idTipoUsuario = 3
                AND (%s = 0 OR li.idEscuela = %s)
                AND (%s = 0 OR pp.idSemestre = %s)
                ORDER BY pe.fecha_registro DESC
                LIMIT 4; 
            """
            cursor.execute(query, (idEscuela, idEscuela, idSemestre, idSemestre))
            rows = cursor.fetchall()
            for row in rows: 
                estudiante_dict = {
                    'codUniversitario': row[0],
                    'nombres': row[1],
                    'correoUSAT': row[2],
                }
                estudiantes.append(estudiante_dict)
    except Exception as e:
        print(f"Error al obtener los estudiantes: {e}")
    finally:
        conexion.close()
    return estudiantes
                
            
def obtener_estudiantes_por_institucion(idEscuela, idSemestre): 
    conexion = obtener_conexion()
    instituciones = []
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT 
                    COALESCE(ins.razonSocial, 'Sin asignar') AS razonSocial, 
                    COUNT(ins.idPersona) AS cantidad
                FROM  persona pe
                INNER JOIN usuario usu ON usu.idUsuario = pe.idUsuario
                LEFT JOIN practicas_preprofesionales pp ON pe.idPersona = pp.idPersona
                LEFT JOIN institucion ins ON ins.numDoc = pp.numDocInstitucion
                LEFT JOIN linea_desarrollo li ON pp.idLinea = li.idLinea
                WHERE usu.idTipoUsuario = 3 
                AND (%s = 0 OR li.idEscuela = %s)
                AND (%s = 0 OR pp.idSemestre = %s)
                GROUP BY COALESCE(ins.razonSocial, 'Sin asignar')
                LIMIT 4;
            """
            cursor.execute(query, (idEscuela, idEscuela, idSemestre, idSemestre))
            rows = cursor.fetchall()
            for row in rows: 
                institucion_dict = {
                    'razonSocial': row[0],
                    'cantidad': row[1],
                }
                instituciones.append(institucion_dict)
    except Exception as e:
        print(f"Error al obtener estudiantes por institución: {e}")
    finally:
        conexion.close()
        
    return instituciones