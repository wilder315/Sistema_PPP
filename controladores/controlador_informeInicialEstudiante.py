from bd import obtener_conexion

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

def agregar_informe_inicial(idPractica, objetivos, plan_trabajo):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Usar 'P' para Pendiente y 'A' para Aprobado (1 carácter)
            estado = 'P'  # El informe inicial empieza como Pendiente

            # Insertar el informe en la tabla 'informe'
            cursor.execute("""
                INSERT INTO informe (estado, idTipoInforme)
                VALUES (%s, %s)
            """, (estado, 1))  # idTipoInforme = 1 para Informe Inicial

            # Obtener el ID del informe recién insertado
            idInforme = cursor.lastrowid

            # Insertar los objetivos en la tabla 'objetivos'
            for objetivo in objetivos:
                cursor.execute("""
                    INSERT INTO objetivos (descripcion, idInforme)
                    VALUES (%s, %s)
                """, (objetivo, idInforme))

            # Insertar el plan de trabajo en la tabla 'plan_trabajo'
            for plan in plan_trabajo:
                semana = plan['semana']
                fecha_inicio = plan['fecha_inicio']
                fecha_fin = plan['fecha_fin']
                actividades = plan['actividad']
                horas = plan['horas']

                cursor.execute("""
                    INSERT INTO plan_trabajo (semana, fechaInicio, fechaFin, actividades, horas, idInforme)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (semana, fecha_inicio, fecha_fin, actividades, horas, idInforme))

            # Confirmar los cambios
            conexion.commit()
            return {"success": True, "message": "Informe inicial agregado correctamente"}
    except Exception as e:
        conexion.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conexion.close()


