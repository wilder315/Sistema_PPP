from bd import obtener_conexion
from service.email_service import EmailService
import logging
import random
import string

class ControladorEmail:
    def __init__(self):
        self.email_service = EmailService()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)


    def obtener_todos_estudiantes_activos(self):
        """Obtiene lista de todos los estudiantes activos"""
        conexion = obtener_conexion()
        if not conexion:
            return None
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT p.nombre, p.apellidos, p.correoP, p.correoUSAT
                    FROM persona p
                    LEFT JOIN usuario u ON p.idUsuario = u.idUsuario
                    WHERE p.estado = 'A' AND u.idTipoUsuario = 3
                    ORDER BY p.apellidos ASC, p.nombre ASC 
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