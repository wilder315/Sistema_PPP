from flask import jsonify
from bd import obtener_conexion
from service.email_service import EmailService

def obtener_jefes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    jefes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT numDoc, apellidos, nombre, correoP, tel1, cargo, idPersona
                FROM persona
                WHERE idUsuario = 2;
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
                SELECT idPersona, numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc
                FROM persona
                WHERE idPersona = %s;
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
        
def obtener_jefe_por_id_modificar(idJefe): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT idPersona, numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc
                FROM persona
                WHERE idPersona = %s;
            """, (idJefe,))    
            rows = cursor.fetchone()
            if rows:
                column_names = [desc[0] for desc in cursor.description]
                jefe_dict = dict(zip(column_names, rows))
                return jefe_dict
            else: 
                return {"error": "Jefe no encontrado"}
    except Exception as e: 
        return {"error": str(e)}
    finally: 
        conexion.close()

def agregar_jefe(numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc, idUsuario): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO persona (numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc, idUsuario)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc, idUsuario))
            conexion.commit()
            return {"mensaje": "Jefe agregado correctamente"}
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
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                DELETE FROM persona
                WHERE idPersona = %s;
            """, (idJefe,))
            conexion.commit()
            return {"mensaje": "Jefe eliminado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()
        
def dar_de_baja_jefe(idPersona):
    if not idPersona: 
        return {"error": "El id del jefe es requerido"}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos"}
    try: 
        with conexion.cursor() as cursor: 
            cursor.execute("UPDATE persona SET estado = 'I' WHERE idPersona = %s", (idPersona,))
            conexion.commit()
            return {"mensaje": "Jefe dado de baja correctamente"}
    except Exception as e: 
        conexion.rollback()
        return {"error": str(e)}
    finally: 
        conexion.close()