from bd import obtener_conexion
from datetime import datetime
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/firmas'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_archivo(archivo):
    if archivo and allowed_file(archivo.filename):
        filename = secure_filename(archivo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        archivo.save(filepath)
        return filepath
    return None

class ControladorFichaEvaluacion:
    
    @classmethod
    def obtener_datos_estudiante(cls, busqueda, modo='busqueda'):
        conexion = obtener_conexion()
        try:
            with conexion.cursor() as cursor:
                if modo == 'busqueda':
                    cursor.execute("""
                        SELECT DISTINCT 
                            p.idPersona as id,
                            CONCAT(p.nombre, ' ', p.apellidos, ' - ', e.nombre) as nombre_completo
                        FROM persona p
                        INNER JOIN usuario u ON p.idUsuario = u.idUsuario
                        INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                        WHERE (LOWER(p.nombre) LIKE LOWER(%s) OR LOWER(p.apellidos) LIKE LOWER(%s))
                        AND p.estado = 'A'
                        AND u.idTipoUsuario = 3
                        LIMIT 10
                    """, (f"%{busqueda}%", f"%{busqueda}%"))
                    
                    resultados = cursor.fetchall()
                    return {"estudiantes": [dict(zip(['id', 'nombre_completo'], r)) for r in resultados]}
                
                else:  # modo selección
                    # Convertir el ID a entero de manera segura
                    try:
                        id_estudiante = int(busqueda)
                    except (ValueError, TypeError):
                        return {"error": "ID de estudiante inválido"}
                        
                    cursor.execute("""
                        SELECT 
                            pp.idPractica,
                            CONCAT(p.nombre, ' ', p.apellidos) as nombres_estudiante,
                            e.nombre as escuela_profesional,
                            CONCAT('Del ', DATE_FORMAT(pp.fechaInicio, '%%d/%%m/%%Y'), ' Al ', 
                                DATE_FORMAT(pp.fechaFin, '%%d/%%m/%%Y')) as periodo_practicas,
                            pp.area as area_desempeno,
                            i.razonSocial as nombre_empresa,
                            i.direccion as direccion_empresa,
                            CONCAT(resp.nombre, ' ', resp.apellidos) as nombre_responsable,
                            resp.correoP as correo_responsable
                        FROM persona p
                        INNER JOIN practicas_preprofesionales pp ON p.idPersona = pp.idPersona
                        INNER JOIN escuela e ON p.idEscuela = e.idEscuela
                        INNER JOIN institucion i ON pp.numDocInstitucion = i.numDoc
                        LEFT JOIN persona resp ON i.idPersona = resp.idPersona
                        WHERE p.idPersona = %s
                        AND pp.estadoVigencia = 'P'
                        LIMIT 1
                    """, (id_estudiante,))
                    
                    resultado = cursor.fetchone()
                    if not resultado:
                        return {"error": "No se encontraron prácticas vigentes para el estudiante"}
                    
                    datos = dict(zip([
                        'idPractica', 'nombres_estudiante', 'escuela_profesional',
                        'periodo_practicas', 'area_desempeno', 'nombre_empresa',
                        'direccion_empresa', 'nombre_responsable', 'correo_responsable'
                    ], resultado))
                    
                    return datos
                        
        except Exception as e:
            print("Error en la consulta:", str(e))
            return {"error": str(e)}
        finally:
            conexion.close()

    @classmethod
    def guardar_ficha_evaluacion(cls, datos_ficha, firma=None):
        conexion = obtener_conexion()
        if not conexion:
            return {"error": "No se pudo establecer conexión con la base de datos."}
        
        try:
            
            with conexion.cursor() as cursor:
                # Procesar la firma si se proporcionó
                firma_url = None
                if firma:
                    firma_url = guardar_archivo(firma)
                    if not firma_url:
                        raise Exception("Error al guardar la firma")
                    
                cursor.execute("""
                    INSERT INTO ficha_evaluacion (
                        idPractica, nombres_estudiante, escuela_profesional, 
                        periodo_practicas, area_desempeno, nombre_empresa, 
                        direccion_empresa, nombre_responsable, correo_responsable,
                        fecha_evaluacion, firma, estado,
                        -- Características evaluadas
                        responsabilidad, proactividad, comunicacion_asertiva,
                        trabajo_equipo, compromiso_calidad, organizacion_trabajo,
                        puntualidad_asistencia,
                        -- Resultados de aprendizaje
                        resultado1, calificacion_resultado1,
                        resultado2, calificacion_resultado2,
                        resultado3, calificacion_resultado3,
                        resultado4, calificacion_resultado4,
                        resultado5, calificacion_resultado5,
                        resultado6, calificacion_resultado6,
                        resultado7, calificacion_resultado7,
                        resultado8, calificacion_resultado8,
                        resultado9, calificacion_resultado9,
                        resultado10, calificacion_resultado10,
                        -- Conclusiones
                        conclusiones, idTipoInforme
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'P',
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                        %s, %s
                    )
                """, (
                    datos_ficha['idPractica'],
                    datos_ficha['nombres_estudiante'],
                    datos_ficha['escuela_profesional'],
                    datos_ficha['periodo_practicas'],
                    datos_ficha['area_desempeno'],
                    datos_ficha['nombre_empresa'],
                    datos_ficha['direccion_empresa'],
                    datos_ficha['nombre_responsable'],
                    datos_ficha['correo_responsable'],
                    datetime.now().date(),
                    firma_url,
                    # Características evaluadas
                    datos_ficha.get('responsabilidad'),
                    datos_ficha.get('proactividad'),
                    datos_ficha.get('comunicacion_asertiva'),
                    datos_ficha.get('trabajo_equipo'),
                    datos_ficha.get('compromiso_calidad'),
                    datos_ficha.get('organizacion_trabajo'),
                    datos_ficha.get('puntualidad_asistencia'),
                    # Resultados de aprendizaje
                    datos_ficha.get('resultado1'), datos_ficha.get('calificacion_resultado1'),
                    datos_ficha.get('resultado2'), datos_ficha.get('calificacion_resultado2'),
                    datos_ficha.get('resultado3'), datos_ficha.get('calificacion_resultado3'),
                    datos_ficha.get('resultado4'), datos_ficha.get('calificacion_resultado4'),
                    datos_ficha.get('resultado5'), datos_ficha.get('calificacion_resultado5'),
                    datos_ficha.get('resultado6'), datos_ficha.get('calificacion_resultado6'),
                    datos_ficha.get('resultado7'), datos_ficha.get('calificacion_resultado7'),
                    datos_ficha.get('resultado8'), datos_ficha.get('calificacion_resultado8'),
                    datos_ficha.get('resultado9'), datos_ficha.get('calificacion_resultado9'),
                    datos_ficha.get('resultado10'), datos_ficha.get('calificacion_resultado10'),
                    # Conclusiones
                    datos_ficha.get('conclusiones'),
                    5
                ))
                conexion.commit()
                return {"mensaje": "Ficha de evaluación guardada correctamente"}
        except Exception as e:
            conexion.rollback()
            return {"error": str(e)}
        finally:
            conexion.close()

    @classmethod
    def obtener_fichas_evaluacion(cls, id_practica=None):
        conexion = obtener_conexion()
        if not conexion:
            return {"error": "No se pudo establecer conexión con la base de datos."}
        
        try:
            with conexion.cursor() as cursor:
                if id_practica:
                    cursor.execute("""
                        SELECT 
                            fe.idFichaEvaluacion,
                            fe.nombres_estudiante,
                            fe.escuela_profesional,
                            fe.nombre_empresa,
                            fe.fecha_evaluacion,
                            fe.estado
                        FROM ficha_evaluacion fe
                        WHERE fe.idPractica = %s
                        ORDER BY fe.fecha_evaluacion DESC
                    """, (id_practica,))
                else:
                    cursor.execute("""
                        SELECT 
                            fe.idFichaEvaluacion,
                            fe.nombres_estudiante,
                            fe.escuela_profesional,
                            fe.nombre_empresa,
                            fe.fecha_evaluacion,
                            fe.estado
                            END as estado
                        FROM ficha_evaluacion fe
                        ORDER BY fe.fecha_evaluacion DESC
                    """)
                
                resultados = cursor.fetchall()
                columnas = ['idFichaEvaluacion', 'nombres_estudiante', 'escuela_profesional', 
                        'nombre_empresa', 'fecha_evaluacion', 'estado']
                return [dict(zip(columnas, resultado)) for resultado in resultados]
        except Exception as e:
            return {"error": str(e)}
        finally:
            conexion.close()
            
    @classmethod
    def obtener_ficha_por_id(cls, id_ficha):
        """Obtiene todos los datos de una ficha de evaluación específica"""
        conexion = obtener_conexion()
        if not conexion:
            return {"error": "No se pudo establecer conexión con la base de datos."}
        
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        fe.idFichaEvaluacion,
                        fe.idPractica,
                        fe.nombres_estudiante,
                        fe.escuela_profesional,
                        fe.periodo_practicas,
                        fe.area_desempeno,
                        fe.nombre_empresa,
                        fe.direccion_empresa,
                        fe.nombre_responsable,
                        fe.correo_responsable,
                        DATE_FORMAT(fe.fecha_evaluacion, '%%d/%%m/%%Y') as fecha_evaluacion,
                        fe.firma,
                        -- Características evaluadas
                        fe.responsabilidad,
                        fe.proactividad,
                        fe.comunicacion_asertiva,
                        fe.trabajo_equipo,
                        fe.compromiso_calidad,
                        fe.organizacion_trabajo,
                        fe.puntualidad_asistencia,
                        -- Resultados de aprendizaje y sus calificaciones
                        fe.resultado1,
                        fe.calificacion_resultado1,
                        fe.resultado2,
                        fe.calificacion_resultado2,
                        fe.resultado3,
                        fe.calificacion_resultado3,
                        fe.resultado4,
                        fe.calificacion_resultado4,
                        fe.resultado5,
                        fe.calificacion_resultado5,
                        fe.resultado6,
                        fe.calificacion_resultado6,
                        fe.resultado7,
                        fe.calificacion_resultado7,
                        fe.resultado8,
                        fe.calificacion_resultado8,
                        fe.resultado9,
                        fe.calificacion_resultado9,
                        fe.resultado10,
                        fe.calificacion_resultado10,
                        fe.conclusiones,
                        fe.estado
                    FROM ficha_evaluacion fe
                    WHERE fe.idFichaEvaluacion = %s
                """, (id_ficha,))
                
                resultado = cursor.fetchone()
                if not resultado:
                    return {"error": "Ficha de evaluación no encontrada"}
                
                columnas = [
                    'idFichaEvaluacion', 'idPractica', 'nombres_estudiante',
                    'escuela_profesional', 'periodo_practicas', 'area_desempeno',
                    'nombre_empresa', 'direccion_empresa', 'nombre_responsable',
                    'correo_responsable', 'fecha_evaluacion', 'firma',
                    'responsabilidad', 'proactividad', 'comunicacion_asertiva',
                    'trabajo_equipo', 'compromiso_calidad', 'organizacion_trabajo',
                    'puntualidad_asistencia',
                    'resultado1', 'calificacion_resultado1',
                    'resultado2', 'calificacion_resultado2',
                    'resultado3', 'calificacion_resultado3',
                    'resultado4', 'calificacion_resultado4',
                    'resultado5', 'calificacion_resultado5',
                    'resultado6', 'calificacion_resultado6',
                    'resultado7', 'calificacion_resultado7',
                    'resultado8', 'calificacion_resultado8',
                    'resultado9', 'calificacion_resultado9',
                    'resultado10', 'calificacion_resultado10',
                    'conclusiones', 'estado'
                ]
                
                datos = dict(zip(columnas, resultado))
                print(datos)
                # Convertir la ruta de la firma a URL completa si existe
                if datos['firma']:
                    nombre_archivo = os.path.basename(datos['firma'])
                    datos['firma'] = f"/static/uploads/firmas/{nombre_archivo}"
                
                return datos
                
        except Exception as e:
            return {"error": f"Error al obtener la ficha: {str(e)}"}
        finally:
            conexion.close()

    @classmethod
    def actualizar_ficha(cls, id_ficha, datos, firma=None):
        try:
            conexion = obtener_conexion()
            with conexion.cursor() as cursor:
                # Mapeo de campos del formulario a columnas de la BD
                campos_evaluacion = {
                    
                    'nombres_estudiante': 'nombres_estudiante',
                    'escuela_profesional': 'escuela_profesional',
                    'periodo_practicas': 'periodo_practicas',
                    'area_desempeno': 'area_desempeno',
                    
                    'nombre_empresa': 'nombre_empresa',
                    'direccion_empresa': 'direccion_empresa',
                    'nombre_responsable': 'nombre_responsable',
                    'correo_responsable': 'correo_responsable',
                    
                    'responsabilidad': 'responsabilidad',
                    'proactividad': 'proactividad',
                    'comunicacion_asertiva': 'comunicacion_asertiva',
                    'trabajo_equipo': 'trabajo_equipo',
                    'compromiso_calidad': 'compromiso_calidad',
                    'organizacion_trabajo': 'organizacion_trabajo',
                    'puntualidad_asistencia': 'puntualidad_asistencia',
                    'conclusiones': 'conclusiones'
                }
                
                # Construir la lista de actualizaciones
                actualizaciones = []
                valores = []
                
                # Procesar campos de evaluación
                for campo_form, campo_bd in campos_evaluacion.items():
                    if campo_form in datos and datos[campo_form]:
                        actualizaciones.append(f"{campo_bd} = %s")
                        valores.append(datos[campo_form])
                
                # Procesar resultados y calificaciones
                for i in range(1, 11):
                    resultado_key = f'resultado{i}'
                    calificacion_key = f'calificacion_resultado{i}'
                    
                    if resultado_key in datos and datos[resultado_key]:
                        actualizaciones.append(f"{resultado_key} = %s")
                        valores.append(datos[resultado_key])
                    
                    if calificacion_key in datos and datos[calificacion_key]:
                        actualizaciones.append(f"{calificacion_key} = %s")
                        valores.append(datos[calificacion_key])
                
                # Procesar firma si existe
                if firma:
                    ruta_firma = guardar_archivo(firma)
                    if ruta_firma:
                        actualizaciones.append("firma = %s")
                        valores.append(ruta_firma)
                
                if not actualizaciones:
                    return {"error": "No hay campos para actualizar"}
                
                # Agregar el ID a los valores
                valores.append(id_ficha)
                
                # Construir y ejecutar la consulta SQL
                sql = f"""
                    UPDATE ficha_evaluacion 
                    SET {', '.join(actualizaciones)}
                    WHERE idFichaEvaluacion = %s 
                    AND estado = 'P'
                """
                
                cursor.execute(sql, valores)
                conexion.commit()
                
                if cursor.rowcount == 0:
                    return {"error": "No se encontró la ficha o no se realizaron cambios"}
                    
                return {"mensaje": "Ficha actualizada correctamente"}
                    
        except Exception as e:
            if conexion:
                conexion.rollback()
            return {"error": f"Error al actualizar la ficha: {str(e)}"}
        finally:
            if conexion:
                conexion.close()