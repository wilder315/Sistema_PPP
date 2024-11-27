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
                SELECT i.numDoc, i.razonSocial, i.tel, i.correo, 
                    CONCAT(p.apellidos, ' ', p.nombre) AS jefe, 
                    IFNULL(CONCAT(i.direccion, ', ', u.ciudad, ', ', u.pais), 'Sin ubicación') AS ubicacion 
                FROM institucion i
                INNER JOIN persona p ON i.idPersona = p.idPersona
                INNER JOIN tipo_documento td ON i.idTipoDoc = td.idTipoDoc
                LEFT JOIN ubicacion u ON u.idUbicacion = i.idUbicacion
                ORDER BY i.razonSocial ASC
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

def obtener_empresas(): 
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    instituciones = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.numDoc as idEmpresa, i.razonSocial as nombre
                FROM institucion i
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
            cursor.execute("""
                SELECT p.apellidos, p.nombre, i.giro, p.cargo, i.direccion , i.razonSocial
                FROM persona p 
                INNER JOIN institucion i ON p.idPersona = i.idPersona 
                WHERE i.numdoc = %s
            """, (ruc,))
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

def obtener_jefes():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    jefes = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.idPersona, CONCAT(p.apellidos, ' ', p.nombre) AS jefe
                FROM persona p 
                LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                WHERE u.idTipoUsuario = 4 ORDER BY jefe ASC
            """
            )
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

def obtener_institucion_por_numdoc(numDoc):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT i.numDoc, i.razonSocial, i.giro, i.direccion, i.tel, i.correo, 
                       i.idUbicacion AS ubicacion, p.idPersona AS jefe, i.idTipoDoc, 
                       u.latitud, u.longitud  -- Agregar latitud y longitud
                FROM institucion i
                INNER JOIN persona p ON i.idPersona = p.idPersona
                INNER JOIN tipo_documento td ON i.idTipoDoc = td.idTipoDoc
                LEFT JOIN ubicacion u ON u.idUbicacion = i.idUbicacion
                WHERE i.numDoc = %s
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

def agregar_institucion(numDoc, giro, razonSocial, direccion, tel, correo, idPersona, idTipoDoc, pais, ciudad, latitud, longitud):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT idUbicacion 
                FROM ubicacion 
                WHERE pais = %s AND ciudad = %s AND latitud = %s AND longitud = %s
            """, (pais, ciudad, latitud, longitud))
            ubicacion_existente = cursor.fetchone()      
            if ubicacion_existente:
                idUbicacion = ubicacion_existente[0]
            else:
                cursor.execute("""
                    INSERT INTO ubicacion (pais, ciudad, latitud, longitud) 
                    VALUES (%s, %s, %s, %s)
                """, (pais, ciudad, latitud, longitud))
                conexion.commit()
                idUbicacion = cursor.lastrowid
            cursor.execute("""
                INSERT INTO institucion (numDoc, giro, razonSocial, direccion, tel, correo, idPersona, idTipoDoc, idUbicacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (numDoc, giro, razonSocial, direccion, tel, correo, idPersona, idTipoDoc, idUbicacion))
            conexion.commit()
            return {"mensaje": "Institución agregada correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def modificar_institucion(numDoc, giro, razonSocial, direccion, tel, correo, idPersona, idTipoDoc, pais, ciudad, latitud, longitud):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT idUbicacion 
                FROM ubicacion 
                WHERE pais = %s AND ciudad = %s AND latitud = %s AND longitud = %s
            """, (pais, ciudad, latitud, longitud))
            ubicacion_existente = cursor.fetchone()

            if ubicacion_existente:
                idUbicacion = ubicacion_existente[0]
            else:
                cursor.execute("""
                    INSERT INTO ubicacion (pais, ciudad, latitud, longitud) 
                    VALUES (%s, %s, %s, %s)
                """, (pais, ciudad, latitud, longitud))
                conexion.commit()
                idUbicacion = cursor.lastrowid
            cursor.execute("""
                UPDATE institucion 
                SET razonSocial = %s, giro = %s, direccion = %s, tel = %s, correo = %s, 
                    idPersona = %s, idTipoDoc = %s, idUbicacion = %s
                WHERE numDoc = %s
            """, (razonSocial, giro, direccion, tel, correo, idPersona, idTipoDoc, idUbicacion, numDoc))
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
            cursor.execute("""
                SELECT COUNT(*)
                FROM practicas_preprofesionales
                WHERE numDocInstitucion = %s
            """, (numDoc,))
            referencia_practica = cursor.fetchone()[0]
            if referencia_practica > 0:
                return {"error": "No se puede eliminar una institución que está vinculada a una práctica."}
            cursor.execute("DELETE FROM institucion WHERE numDoc = %s", (numDoc,))
            conexion.commit()
            return {"mensaje": "Institución eliminada correctamente."}
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_paises():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    paises = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.idPais, p.nombre
                FROM pais p 
                ORDER BY p.nombre ASC
            """
            )
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                pais_dict = dict(zip(column_names, row))
                paises.append(pais_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return paises

def obtener_departamentos(idPais):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    departamentos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.idDepartamento, d.nombre
                FROM departamento d WHERE d.idPais = %s
                ORDER BY d.nombre ASC
            """, (idPais,)
            )
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                departamento_dict = dict(zip(column_names, row))
                departamentos.append(departamento_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return departamentos

def obtener_provincias(idDepartamento):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    provincias = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.idProvincia, p.nombre
                FROM provincia p WHERE p.idDepartamento = %s
                ORDER BY p.nombre ASC
            """, (idDepartamento,)
            )
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                provincia_dict = dict(zip(column_names, row))
                provincias.append(provincia_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return provincias

def obtener_distritos(idProvincia):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."} 
    distritos = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT d.idDistrito, d.nombre
                FROM distrito d WHERE d.idProvincia = %s
                ORDER BY d.nombre ASC
            """, (idProvincia,)
            )
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                distrito_dict = dict(zip(column_names, row))
                distritos.append(distrito_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    return distritos