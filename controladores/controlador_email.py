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

    def generar_contrasena(self, longitud=12):
        """Genera una contraseña aleatoria robusta con letras, dígitos y caracteres especiales"""
        caracteres = string.ascii_letters + string.digits + "@#$%&*"
        return ''.join(random.choice(caracteres) for _ in range(longitud))

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

            # Generar una contraseña aleatoria
            contrasena = self.generar_contrasena()
            print("Contraseña generada:", contrasena)  # Verificar que la contraseña se genera correctamente

            # Enviar el correo de bienvenida con la contraseña generada
            envio_exitoso = self.email_service.enviar_correo_bienvenida(
                nombre=estudiante['nombre'],
                apellidos=estudiante['apellidos'],
                correo_destino=estudiante['correoP'],
                codigo=estudiante['codUniversitario'],
                contrasena=contrasena  # Pasamos la contraseña generada
            )

            if envio_exitoso:
                self.logger.info(f"Correo de bienvenida enviado a {estudiante['correoP']}")
                return {
                    "success": True,
                    "message": "Correo de bienvenida enviado exitosamente",
                    "contrasena": contrasena  # Confirmación de la contraseña generada
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