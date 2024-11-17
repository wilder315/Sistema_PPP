from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario

def obtener_docentes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    docentes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.tel1, p.tel2, 
                       p.correoP, p.correoUSAT, p.cargo, p.estado, g.nombre as genero, td.nombre as tipoDocumento, 
                       e.nombre as escuela, u.username as usuario
                FROM persona p
                LEFT JOIN genero g ON p.idGenero = g.idGenero
                LEFT JOIN tipo_documento td ON p.idTipoDoc = td.idTipoDoc
                LEFT JOIN escuela e ON p.idEscuela = e.idEscuela
                LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE u.idTipoUsuario = 2
                ORDER BY p.apellidos ASC, p.nombre ASC 
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                docente_dict = dict(zip(column_names, row))
                docentes.append(docente_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return docentes

def obtener_docente_por_id(idDocente):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.tel1, p.tel2, p.correoP, 
                p.correoUSAT, p.cargo, p.estado, p.idGenero, p.idTipoDoc, p.idEscuela, u.username
                FROM persona p LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE p.idPersona = %s
            """, (idDocente,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                docente_dict = dict(zip(columnas, row))
                return docente_dict
            else:
                return {"error": "Docente no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_docente(numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idUsuario, idEscuela):
    if not tel2:
        tel2 = None
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO persona (numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idUsuario, idEscuela)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idUsuario, idEscuela))
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
                return {"mensaje": "Docente agregado correctamente y correo enviado"}
            else:
                return {"mensaje": "Docente agregado, pero hubo un error al enviar el correo"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_docente(idDocente, numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idUsuario, idEscuela):
    if not tel2:
        tel2 = None
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE persona
                SET numDoc = %s, nombre = %s, apellidos = %s, tel1 = %s, tel2 = %s, 
                    correoP = %s, correoUSAT = %s, cargo = %s, estado = %s, idGenero = %s, idTipoDoc = %s, 
                    idUsuario = %s, idEscuela = %s
                WHERE idPersona = %s
            """, (numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idUsuario, idEscuela, idDocente))
            conexion.commit()
            return {"mensaje": "Docente modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_docente(idDocente):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idDocente,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al estudiante."}
            cursor.execute("DELETE FROM persona WHERE idPersona = %s", (idDocente,))
            cursor.execute("DELETE FROM usuario WHERE idUsuario = %s", (idUsuario[0],))           
            conexion.commit()
            return {"mensaje": "Docente y usuario eliminados correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_docente(idDocente):
    if not idDocente:
        return {"error": "El ID del docente es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
       with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idDocente,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al estudiante."}
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idDocente,))
            cursor.execute("UPDATE usuario SET estado = 'I' WHERE idUsuario = %s", (idUsuario[0],))    
            conexion.commit()
            return {"mensaje": "Docente dado de baja y usuario inhabilitado correctamente"}  
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()