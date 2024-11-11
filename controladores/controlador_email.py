from bd import obtener_conexion
from service.email_service import EmailService
import logging
from flask import render_template

class ControladorEmail:
    def __init__(self):
        self.email_service = EmailService()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def obtener_datos_estudiante(self, id_persona):
        """Obtiene datos de un estudiante específico"""
        conexion = obtener_conexion()
        if not conexion:
            return None
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT nombre, apellidos, correoP, correoUSAT, codUniversitario
                    FROM persona 
                    WHERE idPersona = %s AND estado = 'A'
                """, (id_persona,))
                row = cursor.fetchone()
                if row:
                    return {
                        'nombre': row[0],
                        'apellidos': row[1],
                        'correoP': row[2],
                        'correoUSAT': row[3],
                        'codUniversitario': row[4]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error al obtener datos del estudiante: {str(e)}")
            return None
        finally:
            conexion.close()

    def enviar_correo_bienvenida_automatico(self, id_persona):
        """Envía correo de bienvenida automático al registrar estudiante"""
        try:
            estudiante = self.obtener_datos_estudiante(id_persona)
            
            if not estudiante:
                return {
                    "success": False,
                    "message": "No se encontró el estudiante"
                }

            envio_exitoso = self.email_service.enviar_correo_bienvenida(
                nombre=estudiante['nombre'],
                apellidos=estudiante['apellidos'],
                correo_destino=estudiante['correoP'],
                codigo=estudiante['codUniversitario']
            )

            if envio_exitoso:
                self.logger.info(f"Correo de bienvenida enviado a {estudiante['correoP']}")
                return {
                    "success": True,
                    "message": "Correo de bienvenida enviado exitosamente"
                }
            else:
                self.logger.error(f"Error al enviar correo de bienvenida a {estudiante['correoP']}")
                return {
                    "success": False,
                    "message": "Error al enviar el correo de bienvenida"
                }

        except Exception as e:
            self.logger.error(f"Error en enviar_correo_bienvenida: {str(e)}")
            return {
                "success": False,
                "message": f"Error en el proceso: {str(e)}"
            }

    def obtener_todos_estudiantes_activos(self):
        """Obtiene lista de todos los estudiantes activos"""
        conexion = obtener_conexion()
        if not conexion:
            return None
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT nombre, apellidos, correoP, correoUSAT
                    FROM persona 
                    WHERE estado = 'A'
                    ORDER BY apellidos, nombre
                """)
                estudiantes = []
                for row in cursor.fetchall():
                    estudiantes.append({
                        'nombre': row[0],
                        'apellidos': row[1],
                        'correoP': row[2],
                        'correoUSAT': row[3]
                    })
                return estudiantes
        except Exception as e:
            self.logger.error(f"Error al obtener estudiantes: {str(e)}")
            return None
        finally:
            conexion.close()

    def enviar_correo_masivo(self, asunto, contenido):
        """Envía correo masivo a todos los estudiantes activos"""
        try:
            estudiantes = self.obtener_todos_estudiantes_activos()
            
            if not estudiantes:
                return {
                    "success": False,
                    "message": "No se encontraron estudiantes activos"
                }

            correos_exitosos = 0
            correos_fallidos = 0

            for estudiante in estudiantes:
                envio_exitoso = self.email_service.enviar_correo_masivo(
                    correo_destino=estudiante['correoP'],
                    asunto=asunto,
                    contenido=contenido
                )
                
                if envio_exitoso:
                    correos_exitosos += 1
                else:
                    correos_fallidos += 1

            return {
                "success": True,
                "message": f"Proceso completado. Exitosos: {correos_exitosos}, Fallidos: {correos_fallidos}",
                "total_estudiantes": len(estudiantes)
            }

        except Exception as e:
            self.logger.error(f"Error en enviar_correo_masivo: {str(e)}")
            return {
                "success": False,
                "message": f"Error en el proceso: {str(e)}"
            }