from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario
import os
from werkzeug.utils import secure_filename
from datetime import date


UPLOAD_FOLDER = 'static/uploads/firmas'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def agregar_informe_final_empresa(
    idInforme, idPractica, fecha, firma1, responsabilidad, extras, cumpleHoras, objetivos
):
    conexion = obtener_conexion()
    tipoInforme = 4
    estado = 'P'
    
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    if not idPractica or not fecha or not firma1 or not responsabilidad or not cumpleHoras:
        return {"error": "Faltan datos obligatorios para registrar el informe final."}
    
    try:
        with conexion.cursor() as cursor:
            if idInforme:  # Si `idInforme` está presente, actualizamos el informe existente
                cursor.execute("""
                    UPDATE informe
                    SET estado = %s, fecha = %s, firma1 = %s, responsabilidad = %s, extras = %s, cumpleHoras = %s
                    WHERE idInforme = %s
                """, (
                    estado, fecha, firma1, responsabilidad, extras, cumpleHoras, idInforme
                ))
            else:  # Si no hay `idInforme`, creamos uno nuevo
                cursor.execute("""
                    INSERT INTO informe (
                        estado, fecha, firma1, idTipoInforme, responsabilidad, extras, cumpleHoras
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    estado, fecha, firma1, tipoInforme, responsabilidad, extras, cumpleHoras
                ))
                idInforme = cursor.lastrowid  # Obtener el ID del nuevo informe
            
            # Modificar los objetivos existentes
            for objetivo in objetivos:
                if 'idObjetivos' in objetivo and 'estado' in objetivo:
                    cursor.execute("""
                        UPDATE objetivos
                        SET estado = %s
                        WHERE idObjetivos = %s
                    """, (objetivo['estado'], objetivo['idObjetivos']))
            
            # Verificar si ya existe la relación en informes_practicas_preprofesionales
            cursor.execute("""
                SELECT COUNT(*) FROM informes_practicas_preprofesionales
                WHERE idPractica = %s AND IidInforme = %s
            """, (idPractica, idInforme))
            relacion_existe = cursor.fetchone()[0] > 0
            
            if not relacion_existe:  # Si no existe, insertamos la relación
                cursor.execute("""
                    INSERT INTO informes_practicas_preprofesionales (idPractica, IidInforme)
                    VALUES (%s, %s)
                """, (idPractica, idInforme))
            
            conexion.commit()
            return {"mensaje": "Informe final de empresa guardado correctamente."}
    except Exception as e:
        print(f"Error al registrar o modificar el informe final: {str(e)}")
        conexion.rollback()
        return {"error": f"Error al registrar o modificar el informe final: {str(e)}"}
    finally:
        conexion.close()

def obtener_objetivos_estudiante(idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Obtener idInforme con idTipoInforme = 1
            cursor.execute("""
                SELECT ip.IidInforme
                FROM informes_practicas_preprofesionales ip
                JOIN informe i ON ip.IidInforme = i.idInforme
                WHERE ip.idPractica = %s AND i.idTipoInforme = 1
            """, (idPractica,))
            informe_resultado = cursor.fetchone()
            if not informe_resultado:
                return {"error": "El estudiante no tiene objetivos registrados."}
            idInforme = informe_resultado[0]

            # Obtener los objetivos relacionados al idInforme
            cursor.execute("""
                SELECT idObjetivos, descripcion, estado
                FROM objetivos
                WHERE idInforme = %s
            """, (idInforme,))
            objetivos = cursor.fetchall()
            if not objetivos:
                return {"error": "No se encontraron objetivos para el informe."}

            # Construir la lista de objetivos como diccionarios
            lista_objetivos = []
            for objetivo in objetivos:
                objetivo_dict = {
                    "idObjetivos": objetivo[0],
                    "descripcion": objetivo[1],
                    "estado": objetivo[2]
                }
                lista_objetivos.append(objetivo_dict)

            return {"objetivos": lista_objetivos}

    except Exception as e:
        print(f"Error al obtener los objetivos del estudiante: {str(e)}")
        return {"error": f"Error al obtener los objetivos del estudiante: {str(e)}"}
    finally:
        conexion.close()

def obtener_estado_informe_final_empresa(idEstudiante):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT i.estado
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                WHERE pp.idPersona = %s
                  AND i.idTipoInforme = 4
                ORDER BY i.fecha DESC
                LIMIT 1
            """, (idEstudiante,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                estado = resultado[0]
                if estado == 'A':  # Aprobado
                    return {"estado": 3}
                elif estado == 'P':  # Pendiente
                    return {"estado": 2}
                elif estado == 'R':  # Rechazado
                    return {"estado": 1}
            return {"estado": 0}  # No tiene informe de tipo 3
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_informe_final_empresa(idEstudiante, idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Obtener los datos principales del informe final de empresa
            cursor.execute("""
                SELECT 
                    i.idInforme, 
                    i.fecha, 
                    i.firma1, 
                    i.responsabilidad, 
                    i.extras, 
                    i.cumpleHoras, 
                    i.estado
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                WHERE ipp.idPractica = %s AND pp.idPersona = %s AND i.idTipoInforme = 4
                ORDER BY i.fecha DESC
                LIMIT 1
            """, (idPractica, idEstudiante))
            informe = cursor.fetchone()
            
            if not informe:
                return {"error": "No se encontró un informe final de empresa asociado a esta práctica."}
            
            # Convertir los datos del informe a un diccionario
            column_names = [desc[0] for desc in cursor.description]
            informe_dict = dict(zip(column_names, informe))
            
            # Obtener los objetivos asociados al informe
            cursor.execute("""
                SELECT idObjetivos, descripcion, estado
                FROM objetivos
                WHERE idInforme = %s
            """, (informe_dict['idInforme'],))
            objetivos = cursor.fetchall()
            informe_dict['objetivos'] = [
                {"idObjetivos": obj[0], "descripcion": obj[1], "estado": obj[2]} for obj in objetivos
            ]
            
            # Verificar relación con prácticas preprofesionales
            cursor.execute("""
                SELECT idPractica, IidInforme
                FROM informes_practicas_preprofesionales
                WHERE idPractica = %s AND IidInforme = %s
            """, (idPractica, informe_dict['idInforme']))
            relacion = cursor.fetchone()
            informe_dict['relacion'] = {
                "idPractica": relacion[0],
                "IidInforme": relacion[1]
            } if relacion else None
            
            return informe_dict
    except Exception as e:
        return {"error": f"Error al obtener el informe final de empresa: {str(e)}"}
    finally:
        conexion.close()


def buscar_estudiantes_practicas(termino_busqueda):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Búsqueda por nombre o apellidos
            sql = """
                SELECT DISTINCT 
                    p.idPersona,
                    p.nombre,
                    p.apellidos,
                    pp.fechaInicio,
                    pp.fechaFin
                FROM persona p
                INNER JOIN practicas_preprofesionales pp ON p.idPersona = pp.idPersona
                WHERE p.estado = 'A' 
                AND pp.idEstado in (1, 2)
                AND (LOWER(p.nombre) LIKE LOWER(%s) 
                OR LOWER(p.apellidos) LIKE LOWER(%s))
                ORDER BY p.apellidos, p.nombre
            """
            termino = f"%{termino_busqueda}%"
            cursor.execute(sql, (termino, termino))
            estudiantes = cursor.fetchall()
            
            # Formatear resultados
            resultados = []
            for est in estudiantes:
                resultados.append({
                    'idPersona': est[0],
                    'nombre': est[1],
                    'apellidos': est[2],
                    'fechaInicio': est[3].strftime('%Y-%m-%d') if est[3] else None,
                    'fechaFin': est[4].strftime('%Y-%m-%d') if est[4] else None,
                    'nombreCompleto': f"{est[2]}, {est[1]}"
                })
            return resultados
            
    except Exception as e:
        print(f"Error en buscar_estudiantes_practicas: {str(e)}")
        return []
    finally:
        conexion.close()        
        
        
def buscar_instituciones(termino_busqueda):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            sql = """
                SELECT 
                    i.numDoc,
                    i.razonSocial,
                    p.nombre,
                    p.apellidos,
                    p.cargo
                FROM institucion i
                INNER JOIN persona p ON i.idPersona = p.idPersona
                WHERE LOWER(i.razonSocial) LIKE LOWER(%s)
                ORDER BY i.razonSocial
            """
            termino = f"%{termino_busqueda}%"
            cursor.execute(sql, (termino,))
            instituciones = cursor.fetchall()
            
            resultados = []
            for inst in instituciones:
                resultados.append({
                    'numDoc': inst[0],
                    'razonSocial': inst[1],
                    'responsable': f"{inst[2]} {inst[3]}",
                    'cargo': inst[4] if inst[4] else 'N/A'
                })
            print(resultados)
            return resultados
            
    except Exception as e:
        print(f"Error en buscar_instituciones: {str(e)}")
        return []
    finally:
        conexion.close()        
        
        

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_archivo(archivo):
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        archivo.save(filepath)
        return filepath
    return None

def guardar_informeInicialEmpresa(aceptacion, labor, labores, firma1, firma2):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Guardar archivos de firmas
            firma1_url = guardar_archivo(firma1)
            firma2_url = guardar_archivo(firma2)
            
            if not firma1_url or not firma2_url:
                raise Exception("Error al guardar las firmas")

            # Preparar el campo labor (labores principales)
            labor_str = ", ".join(labor)
            
            # Preparar el campo labores (labores específicas)
            labores_str = ", ".join(labores)
            
            # Insertar en la tabla INFORMES
            cursor.execute("""
                INSERT INTO informe (
                    aceptacion, estado, labor, fecha, labores, 
                    firma1, firma2, idTipoInforme
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    aceptacion,
                    'P',          # estado
                    labor_str,    # labor (principales)
                    date.today(), # fecha del sistema
                    labores_str,  # labores (específicas)
                    firma1_url,   # firma1
                    firma2_url,   # firma2
                    2            # idTipoInforme = 2
                ))
            
            id_informe = cursor.lastrowid
            
            # Obtener el idPractica del estudiante actual
            cursor.execute("""
                SELECT idPractica 
                FROM practicas_preprofesionales 
                WHERE estadoVigencia = 'P'
                LIMIT 1
            """)
            practica = cursor.fetchone()
            
            if not practica:
                raise Exception("No se encontró una práctica activa")
            
            id_practica = practica[0]
            
            # Insertar en informes_practicas_preprofesionales
            cursor.execute("""
                INSERT INTO informes_practicas_preprofesionales (IidInforme, idPractica)
                VALUES (%s, %s)
                """, (id_informe, id_practica))
            
            conexion.commit()
            return {"message": "Informe guardado correctamente"}
        
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}
    finally:
        conexion.close()

def obtener_informes_empresa():
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Consulta para obtener informes con datos del estudiante
            cursor.execute("""
                SELECT i.idInforme, 
                       CONCAT(p.apellidos, ', ', p.nombre) as estudiante,
                       i.aceptacion,
                       i.estado,
                       i.labor,
                       i.labores,
                       i.firma1,
                       i.firma2,
                       i.fecha
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                INNER JOIN persona p ON pp.idPersona = p.idPersona
                WHERE i.idTipoInforme = 2
                ORDER BY i.idInforme DESC
            """)
            informes = cursor.fetchall()
            
            # Formatear los resultados
            informes_formateados = []
            for informe in informes:
                informes_formateados.append({
                    'idInforme': informe[0],
                    'estudiante': informe[1],
                    'aceptacion': informe[2],
                    'estado': informe[3],
                    'labor': informe[4],
                    'labores': informe[5],
                    'firma1': informe[6],
                    'firma2': informe[7],
                    'fecha': informe[8].strftime('%Y-%m-%d') if informe[8] else None
                })
            return informes_formateados

    except Exception as e:
        print("Error en obtener_informes_empresa:", str(e))
        return []
    finally:
        conexion.close()
           
def obtener_informe_por_id(id_informe):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT i.idInforme, 
                       CONCAT(p.apellidos, ', ', p.nombre) as estudiante,
                       i.aceptacion,
                       i.estado,
                       i.labor,
                       i.labores,
                       i.firma1,
                       i.firma2,
                       i.fecha
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                INNER JOIN persona p ON pp.idPersona = p.idPersona
                WHERE i.idInforme = %s
            """, (id_informe,))
            
            informe = cursor.fetchone()
            if informe:
                return {
                    'idInforme': informe[0],
                    'estudiante': informe[1],
                    'aceptacion': informe[2],
                    'estado': informe[3],
                    'labor': informe[4],
                    'labores': informe[5],
                    'firma1': informe[6],
                    'firma2': informe[7],
                    'fecha': informe[8].strftime('%Y-%m-%d') if informe[8] else None
                }
            return None
    finally:
        conexion.close()

def actualizar_informe(id_informe, fecha, aceptacion, labor, labores, firma1, firma2):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Construir la consulta SQL dinámicamente
            sql = """UPDATE informe 
                     SET fecha = %s,
                         aceptacion = %s,
                         labor = %s,
                         labores = %s"""
            params = [fecha, aceptacion, labor, labores]

            # Procesar firma1 si se proporcionó
            if firma1:
                filename1 = secure_filename(firma1.filename)
                filepath1 = os.path.join('static/uploads/firmas', filename1)
                firma1.save(filepath1)
                sql += ", firma1 = %s"
                params.append(filepath1)

            # Procesar firma2 si se proporcionó
            if firma2:
                filename2 = secure_filename(firma2.filename)
                filepath2 = os.path.join('static/uploads/firmas', filename2)
                firma2.save(filepath2)
                sql += ", firma2 = %s"
                params.append(filepath2)

            sql += " WHERE idInforme = %s"
            params.append(id_informe)

            cursor.execute(sql, tuple(params))
            conexion.commit()

            return {"message": "Informe actualizado correctamente"}
    except Exception as e:
        conexion.rollback()
        print("Error en actualizar_informe:", str(e))
        raise e
    finally:
        conexion.close()