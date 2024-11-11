import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from flask import render_template

class EmailService:
    def __init__(self):
        # Configuración del servidor SMTP de Gmail
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "usatpruebaproyecto@gmail.com"
        self.password = "ayco xcbm jkaw daak"
        

    def _enviar_correo(self, correo_destino: str, asunto: str, contenido_html: str) -> bool:
        """Método base para enviar correos"""
        try:
            mensaje = MIMEMultipart()
            mensaje["From"] = self.sender_email
            mensaje["To"] = correo_destino
            mensaje["Subject"] = asunto
            mensaje.attach(MIMEText(contenido_html, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                server.sendmail(self.sender_email, correo_destino, mensaje.as_string())
            print(f"Correo enviado exitosamente a: {correo_destino}")    
            return True
        except Exception as e:
            print(f"Error al enviar correo: {str(e)}")
            return False

    def enviar_correo_bienvenida(self, 
                                nombre: str, 
                                apellidos: str, 
                                correo_destino: str, 
                                codigo: Optional[str] = None) -> bool:
        """Envía correo de bienvenida automático"""
        try:
            # Usar template de bienvenida
            contenido_html = render_template(
                'emails/bienvenida.html',
                nombre=nombre,
                apellidos=apellidos,
                codigo=codigo
            )
            
            return self._enviar_correo(
                correo_destino=correo_destino,
                asunto="Bienvenido al Sistema de Prácticas Pre-Profesionales",
                contenido_html=contenido_html
            )
        except Exception as e:
            print(f"Error en correo de bienvenida: {str(e)}")
            return False

    def enviar_correo_masivo(self, 
                            correo_destino: str, 
                            asunto: str, 
                            contenido: str) -> bool:
        """Envía correo masivo personalizado"""
        try:
            # Usar template para correos masivos
            contenido_html = render_template(
                'emails/correo_masivo.html',
                contenido=contenido
            )
            
            return self._enviar_correo(
                correo_destino=correo_destino,
                asunto=asunto,
                contenido_html=contenido_html
            )
        except Exception as e:
            print(f"Error en correo masivo: {str(e)}")
            return False