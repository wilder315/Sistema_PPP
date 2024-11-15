import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "usatpruebaproyecto@gmail.com"
        self.password = "tu_contraseña_de_gmail"

    def enviar_correo_bienvenida(self, nombre, apellidos, correo_destino, codigo, contrasena):
        """Envía correo de bienvenida automático con la contraseña generada"""
        try:
            contenido_html = render_template(
                'emails/bienvenida.html',
                nombre=nombre,
                apellidos=apellidos,
                codigo=codigo,
                contrasena=contrasena
            )
            return self._enviar_correo(
                correo_destino=correo_destino,
                asunto="Bienvenido al Sistema de Prácticas Pre-Profesionales",
                contenido_html=contenido_html
            )
        except Exception as e:
            print(f"Error en correo de bienvenida: {str(e)}")
            return False

    def _enviar_correo(self, correo_destino, asunto, contenido_html):
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