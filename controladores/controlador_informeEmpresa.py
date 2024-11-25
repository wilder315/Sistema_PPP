from bd import obtener_conexion
from service.email_service import EmailService
import controladores.controlador_usuario as controlador_usuario

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