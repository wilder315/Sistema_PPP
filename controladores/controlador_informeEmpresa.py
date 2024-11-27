from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario
import os
from werkzeug.utils import secure_filename
from datetime import date


UPLOAD_FOLDER = 'static/uploads/firmas'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def guardar_informeFinalEmpresa(numDoc, area_desarrollo, texto_responsabilidad, texto_otros_aspectos, file_path, cumplimiento_objetivos, fecha): 
    
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            #obtener el idPractica de la tabla PracticaPrefrofesional usando el DNI
            cursor.execute("""
                SELECT idPractica 
                FROM practicas_preprofesionales pp
                INNER JOIN persona pe ON pp.idPersona = pe.idPersona
                WHERE pe.idPersona = %s""", (numDoc))
            practica = cursor.fetchone()
            
            if not practica: 
                return {"error": "No se encontró la práctica."}
            
            idPractica = practica[0]
            
            #Insertar en la tabla INFORMES
            cursor.execute("""
                INSERT INTO informe (aceptacion, estado, labor, cumplehoras, responsabilidad, extras, idTipoInforme, fecha, firma1)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,('ACEPTADO', 'P', area_desarrollo, 'S', texto_responsabilidad, texto_otros_aspectos, 4, fecha, file_path))
            
            print("se ejecuto el insert en informe")
            
            #obtener el id del nuevo informe 
            cursor.execute("SELECT inf.idInforme FROM informe inf where inf.idInforme = LAST_INSERT_ID()")
            practica_informe = cursor.fetchone()
            
            idInforme = practica_informe[0]
            
            #verificamos del valor de idInforme
            if not idInforme: 
                return {"error": "No se pudo obtener el id del informe."}
            
            #print(f"id del informe generado: {idInforme}")
            
            #insertar en la tabla OBJETIVOS
            cursor.execute("""
                    INSERT INTO objetivos (descripcion, idInforme)
                    VALUES (%s,%s)
            """, (cumplimiento_objetivos,idInforme))
            
            #insertar en la tabla informes_practicas_preprofesionales
            cursor.execute("""
                INSERT INTO informes_practicas_preprofesionales (IidInforme, idPractica)
                VALUES (%s, %s)
            """, (idInforme, idPractica))
            
            #actualizar el idEstado en la tabla practicas_preprofesionales
            cursor.execute("""
                UPDATE practicas_preprofesionales
                SET idEstado = 4 
                WHERE idPractica = %s
            """, (idPractica,))
            
            conexion.commit()
            
            return {"message": "Informe guardado correctamente."}
        
    except Exception as e:
        conexion.rollback()
        return {"error": str(e)}    
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
                AND pp.idEstado = 1 
                AND pp.estadoVigencia = 'A'
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
                    aceptacion,   # aceptacion
                    'A',          # estado
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
                WHERE estadoVigencia = 'A'
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

def guardar_archivo(archivo):
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        archivo.save(filepath)
        return filepath
    return None


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
                WHERE i.idTipoInforme = 2 and i.estado = 'A'
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