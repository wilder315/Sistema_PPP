from bd import obtener_conexion
from datetime import datetime

def obtener_instituciones():
    conexion = obtener_conexion()
    instituciones = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT numDoc, razonSocial FROM institucion")
            instituciones = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener instituciones: {e}")
    finally:
        conexion.close()
    return instituciones


def obtener_responsable_institucion(numDoc):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    institucion.razonSocial AS Institucion,
                    persona.nombre,
                    persona.apellidos,
                    persona.cargo
                FROM 
                    institucion
                JOIN 
                    persona ON institucion.idPersona = persona.idPersona
                WHERE
                    institucion.numDoc = %s
            """, (numDoc,))
            row = cursor.fetchone()
            if row:
                return {
                    "success": True,
                    "nombre_responsable": row[0],
                    "apellido_responsable": row[1],
                    "cargo_responsable": row[2]
                }
            else:
                return {"success": False, "message": "No se encontró el responsable para la institución seleccionada."}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conexion.close()

def agregar_informe_inicial_estudiante(
    idInforme, idPractica, fecha, objetivos, plan_trabajos, firma1, firma2
):
    conexion = obtener_conexion()
    tipoInforme = 1
    estado = 'P'
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    if not idPractica or not fecha or not firma1 or not firma2:
        return {"error": "Faltan datos obligatorios para registrar el informe inicial."}
    try:
        with conexion.cursor() as cursor:
            if idInforme:  # Si `idInforme` está presente, actualizamos el informe existente
                cursor.execute("""
                    UPDATE informe
                    SET estado = %s, fecha = %s, firma1 = %s, firma2 = %s
                    WHERE idInforme = %s
                """, (
                    estado, fecha, firma1, firma2, idInforme
                ))
                # Eliminar objetivos y plan de trabajo anteriores
                cursor.execute("DELETE FROM objetivos WHERE idInforme = %s", (idInforme,))
                cursor.execute("DELETE FROM plan_trabajo WHERE idInforme = %s", (idInforme,))
            else:  # Si no hay `idInforme`, creamos uno nuevo
                cursor.execute("""
                    INSERT INTO informe (
                        estado, fecha, firma1, firma2, idTipoInforme
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    estado, fecha, firma1, firma2, tipoInforme
                ))
                idInforme = cursor.lastrowid  # Obtener el ID del nuevo informe
            
            # Insertar los nuevos objetivos
            for objetivo in objetivos:
                cursor.execute("""
                    INSERT INTO objetivos (descripcion, idInforme)
                    VALUES (%s, %s)
                """, (objetivo, idInforme))
            
            # Insertar los nuevos planes de trabajo
            for plan_trabajo in plan_trabajos:
                if not all(key in plan_trabajo for key in ['semana', 'fechaInicio', 'fechaFin', 'actividades', 'horas']):
                    return {"error": "El plan de trabajo no tiene todos los campos requeridos."}
                cursor.execute("""
                    INSERT INTO plan_trabajo (semana, fechaInicio, fechaFin, actividades, horas, idInforme)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    plan_trabajo['semana'],
                    plan_trabajo['fechaInicio'],
                    plan_trabajo['fechaFin'],
                    plan_trabajo['actividades'],
                    plan_trabajo['horas'],
                    idInforme
                ))
            
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
            return {"mensaje": "Informe inicial de estudiante registrado correctamente."}
    except Exception as e:
        print(f"Error al registrar o modificar el informe inicial: {str(e)}")
        conexion.rollback()
        return {"error": f"Error al registrar o modificar el informe inicial: {str(e)}"}
    finally:
        conexion.close()


def obtener_practicas_informe_inicial():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    practicas = []
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT 
                    p.idPractica,
                    CONCAT(pe.nombre, ' ', pe.apellidos) AS estudiante,
                    CONCAT(p.fechaInicio,'') AS fechaInicio,
                    CONCAT(p.fechaFin,'') AS fechaFin,
                    CASE 
                        WHEN p.modalidad = 'P' THEN 'Presencial'
                        WHEN p.modalidad = 'V' THEN 'Virtual'
                        WHEN p.modalidad = 'M' THEN 'Mixta'
                        ELSE 'Desconocida'
                    END AS modalidad,
                    p.area,
                    i.razonSocial AS institucion,
                    s.nombre AS semestre
                FROM practicas_preprofesionales p
                JOIN persona pe ON p.idPersona = pe.idPersona
                JOIN institucion i ON p.numDocInstitucion = i.numDoc
                JOIN semestre_academico s ON p.idSemestre = s.idSemestre
                WHERE p.estadoVigencia = 'P'
            """
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                practica_dict = dict(zip(column_names, row))
                practicas.append(practica_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    # NO uses jsonify() aquí, solo retorna la lista directamente
    return practicas

def agregar_informe_inicial_empresa(idPractica, nombre_empresa, responsable, cargo_responsable, nombre_estudiante, apellido_estudiante, fecha_inicio, fecha_fin, aceptacion, labores):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Estado inicial del informe es 'Pendiente'
            estado = 'P'

            # Insertar en la tabla 'informe' con idTipoInforme = 2 para "Informe Inicial Empresa"
            cursor.execute("""
                INSERT INTO informe (estado, idTipoInforme, aceptacion)
                VALUES (%s, %s, %s)
            """, (estado, 2, aceptacion))

            # Obtener el ID del informe recién insertado
            idInforme = cursor.lastrowid

            # Insertar la relación en la tabla 'informes_practicas_preprofesionales'
            cursor.execute("""
                INSERT INTO informes_practicas_preprofesionales (IidInforme, idPractica)
                VALUES (%s, %s)
            """, (idInforme, idPractica))


            # Confirmar los cambios
            conexion.commit()
            return {"success": True, "message": "Informe inicial (Empresa) agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conexion.close()

def agregar_informe_final_estudiante(
        idInforme, idPractica, fecha_entrega, introduccion, cantidad_trabajadores, mision, vision,
        infraestructura_fisica, infraestructura_tecnologica, organigrama, area_trabajo,
        labores_realizadas, conclusiones, recomendaciones, bibliografia, anexos, firma1, firma2
    ):
    conexion = obtener_conexion()
    tipoInforme = 3
    estado = 'P'
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            if idInforme:
                cursor.execute("""
                    UPDATE informe
                    SET estado = %s, fecha = %s, introduccion = %s, trabajadores = %s,
                        mision = %s, vision = %s, infFisica = %s, infTecnologica = %s,
                        organigrama = %s, area = %s, labores = %s, anexos = %s,
                        bibliografia = %s, firma1 = %s, firma2 = %s
                    WHERE idInforme = %s
                """, (
                    estado, fecha_entrega, introduccion, cantidad_trabajadores, mision, vision,
                    infraestructura_fisica, infraestructura_tecnologica, organigrama, area_trabajo,
                    labores_realizadas, anexos, bibliografia, firma1, firma2, idInforme
                ))
                cursor.execute("""
                    DELETE FROM adicionales WHERE idInforme = %s
                """, (idInforme,))
                for conclusion in conclusiones:
                    cursor.execute("""
                        INSERT INTO adicionales (tipo, descripcion, idInforme)
                        VALUES (%s, %s, %s)
                    """, ('C', conclusion, idInforme))
                for recomendacion in recomendaciones:
                    cursor.execute("""
                        INSERT INTO adicionales (tipo, descripcion, idInforme)
                        VALUES (%s, %s, %s)
                    """, ('R', recomendacion, idInforme))
                conexion.commit()
                return {"mensaje": "Informe final de estudiante actualizado correctamente."}
            else:
                cursor.execute("""
                    INSERT INTO informe (
                        estado, fecha, introduccion, trabajadores, mision, vision, 
                        infFisica, infTecnologica, organigrama, area, labores, anexos, 
                        bibliografia, idTipoInforme, firma1, firma2
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    estado, fecha_entrega, introduccion, cantidad_trabajadores, mision, vision,
                    infraestructura_fisica, infraestructura_tecnologica, organigrama, area_trabajo,
                    labores_realizadas, anexos, bibliografia, tipoInforme, firma1, firma2
                ))
                idInforme = cursor.lastrowid
                for conclusion in conclusiones:
                    cursor.execute("""
                        INSERT INTO adicionales (tipo, descripcion, idInforme)
                        VALUES (%s, %s, %s)
                    """, ('C', conclusion, idInforme))
                for recomendacion in recomendaciones:
                    cursor.execute("""
                        INSERT INTO adicionales (tipo, descripcion, idInforme)
                        VALUES (%s, %s, %s)
                    """, ('R', recomendacion, idInforme))
                cursor.execute("""
                    INSERT INTO informes_practicas_preprofesionales (idPractica, IidInforme)
                    VALUES (%s, %s)
                """, (idPractica, idInforme))
                conexion.commit()
                return {"mensaje": "Informe final de estudiante registrado correctamente."}
    except Exception as e:
        conexion.rollback()
        return {"error": f"Error al registrar o modificar el informe: {str(e)}"}
    finally:
        conexion.close()

def obtener_informe_final_estudiante(idEstudiante, idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    i.estado, i.fecha, i.introduccion, i.trabajadores, i.mision, i.vision, 
                    i.infFisica, i.infTecnologica, i.organigrama, i.area, i.labores, 
                    i.anexos, i.bibliografia, i.idInforme, i.firma1, i.firma2
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                WHERE pp.idPersona = %s AND pp.idPractica = %s AND i.idTipoInforme = 3
                ORDER BY i.fecha DESC
                LIMIT 1
            """, (idEstudiante, idPractica))
            informe = cursor.fetchone()
            if not informe:
                return {"error": "No se encontró un informe final asociado a esta práctica."}         
            column_names = [desc[0] for desc in cursor.description]
            informe_dict = dict(zip(column_names, informe))
            cursor.execute("""
                SELECT tipo, descripcion
                FROM adicionales
                WHERE idInforme = %s
            """, (informe_dict['idInforme'],))
            adicionales = cursor.fetchall()
            conclusiones = [adicional[1] for adicional in adicionales if adicional[0] == 'C']
            recomendaciones = [adicional[1] for adicional in adicionales if adicional[0] == 'R']
            informe_dict['conclusiones'] = conclusiones
            informe_dict['recomendaciones'] = recomendaciones
            return informe_dict
    except Exception as e:
        return {"error": f"Error al obtener el informe: {str(e)}"}
    finally:
        conexion.close()

def agregar_informe_final_empresa(nombre_empresa, responsable, grado_responsable, cargo_responsable,
                                  nombre_estudiante, fecha_inicio, fecha_fin, cumplimiento_objetivos,
                                  cumplimiento_horas, responsabilidad, otros_aspectos, fecha_firma,
                                  firma_responsable, cargo_firma):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            estado = 'P'  # Estado inicial como 'Pendiente'
            tipo_informe = 3  # Tipo de informe: 3 para Informe Final de Empresa

            # Insertar el informe en la tabla 'informe'
            cursor.execute("""
                INSERT INTO informe (estado, idTipoInforme)
                VALUES (%s, %s)
            """, (estado, tipo_informe))

            # Obtener el ID del informe recién insertado
            idInforme = cursor.lastrowid

            # Insertar los detalles del informe en la tabla 'informe_final_empresa'
            cursor.execute("""
                INSERT INTO informe_final_empresa (
                    idInforme, nombre_empresa, responsable, grado_responsable, cargo_responsable,
                    nombre_estudiante, fecha_inicio, fecha_fin, cumplimiento_objetivos,
                    cumplimiento_horas, responsabilidad, otros_aspectos, fecha_firma,
                    firma_responsable, cargo_firma
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (idInforme, nombre_empresa, responsable, grado_responsable, cargo_responsable,
                  nombre_estudiante, fecha_inicio, fecha_fin, cumplimiento_objetivos,
                  cumplimiento_horas, responsabilidad, otros_aspectos, fecha_firma,
                  firma_responsable, cargo_firma))

            # Confirmar los cambios
            conexion.commit()
            return {"success": True, "message": "Informe final de empresa agregado correctamente."}
    except Exception as e:
        conexion.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conexion.close()

   
def obtener_estado_informe_final_estudiante(idEstudiante):
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
                  AND i.idTipoInforme = 3
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

def obtener_informe_inicial_estudiante(idEstudiante, idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}   
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    i.fecha, i.idInforme, i.firma1, i.firma2
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                WHERE pp.idPersona = %s AND pp.idPractica = %s AND i.idTipoInforme = 1
                ORDER BY i.fecha DESC
                LIMIT 1
            """, (idEstudiante, idPractica))
            informe = cursor.fetchone()           
            if not informe:
                return {"error": "No se encontró un informe inicial asociado a esta práctica."}  
            column_names = [desc[0] for desc in cursor.description]
            informe_dict = dict(zip(column_names, informe))
            cursor.execute("""
                SELECT idObjetivos, descripcion
                FROM objetivos
                WHERE idInforme = %s
            """, (informe_dict['idInforme'],))
            objetivos = cursor.fetchall()
            informe_dict['objetivos'] = [
                {"idObjetivos": obj[0], "descripcion": obj[1]} for obj in objetivos
            ]
            cursor.execute("""
                SELECT idPlab, semana, fechaInicio, fechaFin, actividades, horas
                FROM plan_trabajo
                WHERE idInforme = %s
            """, (informe_dict['idInforme'],))
            actividades = cursor.fetchall()
            informe_dict['actividades'] = [
                {
                    "idPlab": act[0],
                    "semana": act[1],
                    "fechaInicio": act[2],
                    "fechaFin": act[3],
                    "actividades": act[4],
                    "horas": act[5],
                } for act in actividades
            ]          
            return informe_dict
    except Exception as e:
        return {"error": f"Error al obtener el informe inicial: {str(e)}"} 
    finally:
        conexion.close()

def obtener_estado_informe_inicial_estudiante(idEstudiante):
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
                  AND i.idTipoInforme = 1
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

def agregar_constancia(idInforme, idPractica, anexos):

    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    if  not idPractica or not anexos:
        return {"error": "Faltan datos obligatorios para registrar la constancia."}

    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT idInforme FROM informe WHERE idInforme = %s", (idInforme,))
            informe_existente = cursor.fetchone()
            
            if informe_existente:
                # Actualizar la constancia en el informe existente
                cursor.execute("""
                    UPDATE informe
                    SET anexos = %s
                    WHERE idInforme = %s
                """, (anexos, idInforme))
                cursor.execute("""
                    INSERT INTO informes_practicas_preprofesionales (idPractica, IidInforme)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE idPractica = VALUES(idPractica)
                """, (idPractica, idInforme))
                
                conexion.commit()
                return {"mensaje": "Constancia de estudio actualizada correctamente."}
            else:
                estado = 'P'
                tipoInforme = 6 
                fecha_actual = datetime.now().strftime('%Y-%m-%d')  # Fecha actual

                cursor.execute("""
                    INSERT INTO informe (estado, fecha, anexos, idTipoInforme)
                    VALUES (%s, %s, %s, %s)
                """, (estado, fecha_actual, anexos, tipoInforme))
                
                # Obtener el nuevo ID de informe
                idInformeNuevo = cursor.lastrowid
                
                # Insertar en la tabla de detalle asociada
                cursor.execute("""
                    INSERT INTO informes_practicas_preprofesionales (idPractica, IidInforme)
                    VALUES (%s, %s)
                """, (idPractica, idInformeNuevo))
                
                conexion.commit()
                return {"mensaje": "Constancia de estudio registrada correctamente.", "idInforme": idInformeNuevo}
    except Exception as e:
        conexion.rollback()
        return {"error": f"Error al registrar o modificar la constancia: {str(e)}"}
    finally:
        conexion.close()

def obtener_estado_constancia(idEstudiante):
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
                  AND i.idTipoInforme = 6
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

def obtener_constancia(idEstudiante, idPractica):
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try:
        with conexion.cursor() as cursor:
            # Consulta para obtener el informe final asociado al estudiante y la práctica
            cursor.execute("""
                SELECT 
                    i.estado, i.anexos, i.idInforme
                FROM informe i
                INNER JOIN informes_practicas_preprofesionales ipp ON i.idInforme = ipp.IidInforme
                INNER JOIN practicas_preprofesionales pp ON ipp.idPractica = pp.idPractica
                WHERE pp.idPersona = %s AND pp.idPractica = %s AND i.idTipoInforme = 6
                ORDER BY i.fecha DESC
                LIMIT 1
            """, (idEstudiante, idPractica))
            informe = cursor.fetchone()
            if not informe:
                return {"error": "No se encontró un informe final asociado a esta práctica."}         
            
            # Crear un diccionario con los resultados
            column_names = [desc[0] for desc in cursor.description]
            informe_dict = dict(zip(column_names, informe))

            return informe_dict
    except Exception as e:
        return {"error": f"Error al obtener el informe: {str(e)}"}
    finally:
        conexion.close()
