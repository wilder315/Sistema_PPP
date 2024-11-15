from flask import Flask
from routers.router_main import router_main  # Importa el Blueprint
from routers.router_facultad import router_facultad
from routers.router_estudiante import router_estudiante
from routers.router_docente import router_docente
from routers.router_escuela import router_escuela
from routers.router_ppp import router_practicas
from routers.router_genero import router_genero
from routers.router_semestre import router_semestre
from routers.router_tipo_practicas import router_tipo_practicas
from routers.router_horas_ppp import router_horas_ppp
from routers.router_linea_desarrollo import router_linea_desarrollo
from routers.router_institucion import router_institucion
from routers.router_estado import router_estado
from routers.router_tipoDocumento import router_tipoDocumento
from routers.router_usuario import router_usuario
from routers.router_tipoPracticas import router_tipoPracticas
from routers.router_informeAlumno import router_informeAlumno
from routers.router_email import router_email

app = Flask(__name__)
app.debug = False
app.secret_key = 'super-secret'

# Registra el Blueprint
app.register_blueprint(router_main)
app.register_blueprint(router_facultad)
app.register_blueprint(router_estudiante)
app.register_blueprint(router_docente)
app.register_blueprint(router_escuela)
app.register_blueprint(router_practicas)
app.register_blueprint(router_genero)
app.register_blueprint(router_semestre)
app.register_blueprint(router_tipo_practicas)
app.register_blueprint(router_horas_ppp)
app.register_blueprint(router_linea_desarrollo)
app.register_blueprint(router_institucion)
app.register_blueprint(router_estado)
app.register_blueprint(router_tipoDocumento)
app.register_blueprint(router_usuario)
app.register_blueprint(router_tipoPracticas)
app.register_blueprint(router_informeAlumno)
app.register_blueprint(router_email)


if __name__ == "__main__":
    app.run(debug=True)