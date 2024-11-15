from bd import obtener_conexion
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import hashlib, random, string, base64, os

AES_KEY = b'\xe3\x93\xafR\x81\x12\xe5\xa3\x0b\xedH\xfb\xab\xf8J\x92\xae\x18\xbf\x9c\xef\x1e\xe7\xb1'

def obtener_usuarios():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    usuarios = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT u.idUsuario, u.username, u.password, u.estado, t.tipo as tipo FROM usuario u INNER JOIN tipo_usuario t ON t.idTipoUsuario = u.idTipoUsuario")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                usuario_dict = dict(zip(column_names, row))
                usuarios.append(usuario_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return usuarios

def obtener_usuario_por_id(idUsuario):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}    
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
            """SELECT 
                u.idUsuario, 
                u.username, 
                u.password, 
                u.estado, 
                u.idTipoUsuario,
                CASE u.idTipoUsuario
                    WHEN '3' THEN 'Practicante'
                    WHEN '2' THEN 'Docente de Apoyo PPP'
                    WHEN '1' THEN 'Director de Escuela'
                    WHEN '4' THEN 'Jefe Directo'
                    ELSE 'Otro'
                END AS tipoUsuario
            FROM 
                usuario u
            WHERE u.idUsuario = %s""", (idUsuario,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                usuario_dict = dict(zip(columnas, row))
                return usuario_dict
            else:
                return {"error": "Facultad no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def generar_username(nombre, apellidos):
    nombre_parts = nombre.strip().split()
    apellido_parts = apellidos.strip().split()
    inicial_nombre = nombre_parts[0][0].lower()
    primer_apellido = apellido_parts[0].lower()
    username = f"{inicial_nombre}{primer_apellido}"
    return username

def generar_contraseña():
    letras = random.choices(string.ascii_letters, k=3)
    numeros = random.choices(string.digits, k=3)
    contraseña = ''.join(letras + numeros)
    random.shuffle(list(contraseña))
    return ''.join(contraseña)

def cifrar_contraseña(password):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()
    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()
    return base64.b64encode(iv + encrypted_password).decode()

def descifrar_contraseña(encrypted_password):
    encrypted_data = base64.b64decode(encrypted_password)
    iv = encrypted_data[:16]
    encrypted_password = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_password = decryptor.update(encrypted_password) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_password = unpadder.update(decrypted_padded_password) + unpadder.finalize()
    return decrypted_password.decode()

def actualizar_contraseña(id_usuario, nueva_password_cifrada):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario
                SET password = %s
                WHERE idUsuario = %s
            """, (nueva_password_cifrada, id_usuario))
            conexion.commit()
            return {"mensaje": "Contraseña actualizada correctamente."}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_usuario(username, estado, idTipoUsuario):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    try:
        contraseña_generada = generar_contraseña()
        password_cifrada = cifrar_contraseña(contraseña_generada)
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuario (username, password, estado, idTipoUsuario)
                VALUES (%s, %s, %s, %s)
            """, (username, password_cifrada, estado, idTipoUsuario))
            conexion.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            idUsuario = cursor.fetchone()[0]

        return {"mensaje": "Usuario agregado correctamente", "idUsuario": idUsuario, "contraseña": contraseña_generada}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_usuario(idUsuario, username, estado, idTipoUsuario):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario
                SET username = %s, estado = %s, idTipoUsuario = %s
                WHERE idUsuario = %s
            """, (username, estado, idTipoUsuario, idUsuario))
            conexion.commit()
            return {"mensaje": "Usuario modificado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_usuario(idUsuario):
    if not idUsuario:
        return {"error": "El ID del usuario es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM usuario WHERE idUsuario = %s", (idUsuario,))
            conexion.commit()
            return {"mensaje": "Usuario eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_usuario(idUsuario):
    if not idUsuario:
        return {"error": "El ID del usuario es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE usuario SET estado = 'I' WHERE idUsuario = %s", (idUsuario,))
            conexion.commit()
            return {"mensaje": "Usuario dada de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_usuarios_estudiantes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    usuarios = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario, username, password FROM usuario where idTipoUsuario = 3")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                usuario_dict = dict(zip(column_names, row))
                usuarios.append(usuario_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return usuarios

def obtener_usuarios_docentes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    usuarios = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idUsuario, username, password FROM usuario where idTipoUsuario = 2")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                usuario_dict = dict(zip(column_names, row))
                usuarios.append(usuario_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return usuarios

def obtener_usuario_con_tipopersona_por_username(username):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT idUsuario, username, estado, password FROM usuario WHERE username =  %s", (username))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def obtener_usuario_por_username(username):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT idusuario, username, password, estado, idpersona FROM usuario WHERE username = %s", (username,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_token(username,token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuario SET token = %s WHERE username = %s",
                       (token,username))
    conexion.commit()
    conexion.close()

def obtener_datos_usuario (id):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT p.nombre, p.apellidos, p.foto FROM persona p inner join usuario u on p.idusuario = u.idusuario WHERE u.idusuario = %s", (id,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def actualizar_datos_usuario(id, nombres, apellidos, n_documento, correo, telefono):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE persona SET nombres = %s, apellidos = %s, n_documento = %s, correo = %s, telefono = %s WHERE idpersona = (SELECT idpersona FROM usuario WHERE idusuario = %s)",
                           (nombres, apellidos, n_documento, correo, telefono, id))
            conexion.commit()
            return {"mensaje": "Datos actualizados correctamente"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_datos_usuario_informe():
    conexion = obtener_conexion()
    usuario_informe = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("select p.nombre, p.apellidos, p.codUniversitario  from persona p inner join usuario u on p.idUsuario = u.idUsuario where u.idTipoUsuario=3")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                usuario_informe_dict = dict(zip(column_names, row))
                usuario_informe.append(usuario_informe_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_tipoUsuarios():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    tipo_usuarios = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM tipo_usuario ORDER BY idTipoUsuario ASC")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                tipo_usuario_dict = dict(zip(column_names, row))
                tipo_usuarios.append(tipo_usuario_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return tipo_usuarios

