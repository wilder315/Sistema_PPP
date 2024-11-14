from bd import obtener_conexion

def obtener_plan_trabajo():
    conexion = obtener_conexion()
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    
    plan_trabajo = []
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM plan_trabajo")
            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()

            for row in rows:
                plan_trabajo_dict = dict(zip(column_names, row))
                plan_trabajo.append(plan_trabajo_dict)
    except Exception as e:
        return {"error": str(e)}
    finally:
        conexion.close()
    
    return plan_trabajo

def agregar_plan_trabajo(semana, fechaInicio, fechaFin, actividades, horas, idInforme):
    #validaciones 
    if not semana or not fechaInicio or not fechaFin or not actividades or not horas or not idInforme: 
        return {"error": "Todos los campos son requeridos."}

    conexion = obtener_conexion() 
    if not conexion:
        return {"error": "No se pudo establecer conexión con la base de datos."}
    try: 
        with conexion.cursor() as cursor:  
            cursor.execute("""
                INSERT INTO plan_trabajo (semana, fechaInicio, fechaFin, actividades, horas, idInforme)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (semana, fechaInicio, fechaFin, actividades, horas, idInforme))
            conexion.commit()
            return {"mensaje": "Plan trabajo agregado correctamente"}
    except Exception as e: 
        conexion.rollback()
        return {"error": str(e)}
    finally: 
        conexion.close()

