from bd import obtener_conexion

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
            "SELECT u.idUsuario, u.username, u.password, u.estado, u.idTipoUsuario FROM usuario u WHERE idUsuario = %s", (idUsuario,))
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

def agregar_usuario(username, password, estado, idTipoUsuario):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuario (username, password, estado, idTipoUsuario)
                VALUES (%s, %s, %s, %s)
            """, (username, password, estado, idTipoUsuario))
            conexion.commit()
            return {"mensaje": "Usuario agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_usuario(idUsuario, username, password, estado, idTipoUsuario):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE usuario
                SET username = %s, password = %s, estado = %s, idTipoUsuario = %s
                WHERE idUsuario = %s
            """, (username, password, estado, idTipoUsuario, idUsuario))
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

