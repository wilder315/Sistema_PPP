from bd import obtener_conexion

def obtener_instituciones():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    instituciones = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.numDoc, i.razonSocial, i.direccion, i.tel, i.correo,
                       d.nombre AS distrito, p.nombre AS jefe, td.nombre AS tipoDocumento
                FROM institucion i
                JOIN distrito d ON i.idDistrito = d.idDistrito
                JOIN persona p ON i.idPersona = p.idPersona
                JOIN tipo_documento td ON i.idTipoDoc = td.idTipoDoc
            """
            )
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                institucion_dict = dict(zip(column_names, row))
                instituciones.append(institucion_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return instituciones

def obtener_jefe(ruc):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    instituciones = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT p.apellidos, p.nombre FROM persona p INNER JOIN institucion i ON p.idPersona = i.idPersona where i.numdoc = %s", (ruc,))
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                institucion_dict = dict(zip(column_names, row))
                instituciones.append(institucion_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return instituciones 


def obtener_institucion_por_numdoc(numDoc):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.numDoc, i.razonSocial, i.direccion, i.tel, i.correo,
                       d.nombre AS distrito, p.nombre AS jefe, td.nombre AS tipoDocumento
                FROM institucion i
                JOIN distrito d ON i.idDistrito = d.idDistrito
                JOIN persona p ON i.idPersona = p.idPersona
                JOIN tipo_documento td ON i.idTipoDoc = td.idTipoDoc WHERE i.numDoc = %s
            """
            , (numDoc,))
            row = cursor.fetchone()
            if row:
                columnas = [desc[0] for desc in cursor.description]
                institucion_dict = dict(zip(columnas, row))
                return institucion_dict
            else:
                return {"error": "Institución no encontrada"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def agregar_institucion(numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO institucion (numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc))
            conexion.commit()
            return {"mensaje": "Institución agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_institucion(numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE institucion 
                SET razonSocial = %s, direccion = %s, tel = %s, correo = %s, 
                    idDistrito = %s, idPersona = %s, idTipoDoc = %s
                WHERE numDoc = %s
            """, (razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc, numDoc))
            conexion.commit()
            return {"mensaje": "Institución modificada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def eliminar_institucion(numDoc):
    if not numDoc:
        return {"error": "El número de documento es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM institucion WHERE numDoc = %s", (numDoc,))
            conexion.commit()
            return {"mensaje": "Institución eliminada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def dar_de_baja_institucion(numDoc):
    if not numDoc:
        return {"error": "El número de documento es requerido."}
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE institucion SET correo = 'I' WHERE numDoc = %s", (numDoc,))
            conexion.commit()
            return {"mensaje": "Institución dada de baja correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

