from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario

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
                        p.idEscuela, u.username
                FROM persona p LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
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
            usuario_data = controlador_usuario.obtener_usuario_por_id(idUsuario)
            if not usuario_data:
                return {"error": "No se pudo obtener el usuario"}
            usuario = usuario_data['username']
            password_descifrada = controlador_usuario.descifrar_contraseña(usuario_data['password'])
            email_service = EmailService()
            envio_exitoso = email_service.enviar_correo_bienvenida(
                nombre=nombre,
                apellidos=apellidos,
                correo_destino=correoP,
                codigo=usuario,
                contrasena=password_descifrada
            )
            if envio_exitoso:
                return {"mensaje": "Estudiante agregado correctamente y correo enviado"}
            else:
                return {"mensaje": "Estudiante agregado, pero hubo un error al enviar el correo"}
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
    if not idEstudiante: 
        return {"error": "El id del jefe es requerido"}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idEstudiante,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al estudiante."}
            cursor.execute("DELETE FROM persona WHERE idPersona = %s", (idEstudiante,))
            cursor.execute("DELETE FROM usuario WHERE idUsuario = %s", (idUsuario[0],))           
            conexion.commit()
            return {"mensaje": "Estudiante y usuario eliminados correctamente"}
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
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idEstudiante,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al estudiante."}
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idEstudiante,))
            cursor.execute("UPDATE usuario SET estado = 'I' WHERE idUsuario = %s", (idUsuario[0],))    
            conexion.commit()
            return {"mensaje": "Estudiante dado de baja y usuario inhabilitado correctamente"}  
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}  
    finally:
        conexion.close()
   
#------------------------ CARLOS DELGADO
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



def obtener_estudiantes_por_genero_escuela():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    e.nombre as Escuela,
                    f.nombre as Facultad,
                    SUM(CASE WHEN g.nombre = 'Masculino' THEN 1 ELSE 0 END) as Varones,
                    SUM(CASE WHEN g.nombre = 'Femenino' THEN 1 ELSE 0 END) as Mujeres,
                    COUNT(*) as Total,
                    ROUND((SUM(CASE WHEN g.nombre = 'Masculino' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as PorcentajeVarones,
                    ROUND((SUM(CASE WHEN g.nombre = 'Femenino' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as PorcentajeMujeres
                FROM persona p
                INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                INNER JOIN facultad f ON e.idFacultad = f.idFacultad
                INNER JOIN genero g ON p.idGenero = g.idGenero
                INNER JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE u.idTipoUsuario = 3 AND p.estado = 'A'
                GROUP BY e.nombre, f.nombre
                ORDER BY f.nombre, e.nombre
            """)
            columnas = [desc[0] for desc in cursor.description]
            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(zip(columnas, row)))
            return resultados
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()        
        

def obtener_estudiantes_por_semestre():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    sa.nombre as Semestre,
                    e.nombre as Escuela,
                    f.nombre as Facultad,
                    COUNT(DISTINCT p.idPersona) as TotalEstudiantes,
                    COUNT(DISTINCT CASE WHEN g.nombre = 'Masculino' THEN p.idPersona END) as Varones,
                    COUNT(DISTINCT CASE WHEN g.nombre = 'Femenino' THEN p.idPersona END) as Mujeres,
                    ROUND((COUNT(DISTINCT CASE WHEN g.nombre = 'Masculino' THEN p.idPersona END) * 100.0 / 
                        COUNT(DISTINCT p.idPersona)), 2) as PorcentajeVarones,
                    ROUND((COUNT(DISTINCT CASE WHEN g.nombre = 'Femenino' THEN p.idPersona END) * 100.0 / 
                        COUNT(DISTINCT p.idPersona)), 2) as PorcentajeMujeres
                FROM practicas_preprofesionales pp
                INNER JOIN persona p ON pp.idPersona = p.idPersona
                INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                INNER JOIN facultad f ON e.idFacultad = f.idFacultad
                INNER JOIN genero g ON p.idGenero = g.idGenero
                INNER JOIN semestre_academico sa ON pp.idSemestre = sa.idSemestre
                WHERE p.estado = 'A'
                GROUP BY sa.nombre, e.nombre, f.nombre
                ORDER BY sa.nombre DESC, f.nombre, e.nombre
            """)
            columnas = [desc[0] for desc in cursor.description]
            resultados = []
            for row in cursor.fetchall():
                resultados.append(dict(zip(columnas, row)))
            return resultados
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()    