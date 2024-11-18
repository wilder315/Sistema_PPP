from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario

def obtener_jefes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    jefes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.numDoc, p.apellidos, p.nombre, p.correoP, p.tel1, p.cargo, p.idPersona
                FROM persona p LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE u.idTipoUsuario = 4
                ORDER BY p.apellidos ASC, p.nombre ASC 
            """)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                jefe_dict = dict(zip(column_names, row))
                jefes.append(jefe_dict)
            
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

    return jefes 

def obtener_jefe_por_id(idJefe): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.idPersona, p.numDoc, p.nombre, p.apellidos, p.tel1, p.correoP, p.cargo, p.estado, p.idGenero, p.idTipoDoc, u.username
                FROM persona p LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE p.idPersona = %s;
            """, (idJefe,))
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                jefe_dict = dict(zip(column_names, row))
                return jefe_dict
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_jefe(numDoc, nombre, apellidos, tel1, correoP, foto, cargo, estado, idGenero, idTipoDoc, idUsuario): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO persona (numDoc, nombre, apellidos, tel1, correoP, foto, cargo, estado, idGenero, idTipoDoc, idUsuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (numDoc, nombre, apellidos, tel1, correoP, foto, cargo, estado, idGenero, idTipoDoc, idUsuario))
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
                return {"mensaje": "Jefe agregado correctamente y correo enviado"}
            else:
                return {"mensaje": "Jefe agregado, pero hubo un error al enviar el correo"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()
        
def modificar_jefe(numDoc, nombre, apellidos, telf1, correoP,cargo, estado, idGenero, idTipoDoc, idPersona):
    if not telf1:
        telf1 = None
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE persona
                SET numDoc = %s, nombre = %s, apellidos = %s, tel1 = %s, correoP = %s, cargo = %s, estado = %s, idGenero = %s, idTipoDoc = %s
                WHERE idPersona = %s;
            """, (numDoc, nombre, apellidos, telf1, correoP, cargo, estado, idGenero, idTipoDoc, idPersona))
            conexion.commit()
            return {"mensaje": "Jefe modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()
        
def eliminar_jefe(idJefe):  
    if not idJefe: 
        return {"error": "El id del jefe es requerido"}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idJefe,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al jefe."}
            cursor.execute("DELETE FROM persona WHERE idPersona = %s", (idJefe,))
            cursor.execute("DELETE FROM usuario WHERE idUsuario = %s", (idUsuario[0],))           
            conexion.commit()
            return {"mensaje": "Jefe y usuario eliminados correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()
        
def dar_de_baja_jefe(idJefe):
    if not idJefe: 
        return {"error": "El id del jefe es requerido"}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos"}
    try: 
        with conexion.cursor() as cursor: 
            cursor.execute("SELECT idUsuario FROM persona WHERE idPersona = %s", (idJefe,))
            idUsuario = cursor.fetchone()
            if not idUsuario:
                return {"error": "No se encontró el usuario asociado al jefe."}
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idJefe,))
            cursor.execute("UPDATE usuario SET estado = 'I' WHERE idUsuario = %s", (idUsuario[0],))    
            conexion.commit()
            return {"mensaje": "Jefe dado de baja y usuario inhabilitado correctamente"}  
    except Exception as e: 
        conexion.rollback()
        return {"error": str(e)}
    finally: 
        conexion.close()