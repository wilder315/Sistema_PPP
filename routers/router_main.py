from flask import Blueprint, render_template, request, redirect, jsonify, make_response, session, url_for, flash
from werkzeug.utils import secure_filename
from bd import obtener_conexion
from bd import obtener_conexion
from functools import wraps
import controladores.controlador_usuario as controlador_usuario
import controladores.controlador_informeAlumno as controlador_informeAlumno
import time
from controladores.controlador_estudiante import obtener_estudiantes_por_fecha, obtener_estadisticas_estudiantes, obtener_ppp_finalizadas

login_attempts = {}
router_main = Blueprint('router_main', __name__)
AES_KEY = b'\xe3\x93\xafR\x81\x12\xe5\xa3\x0b\xedH\xfb\xab\xf8J\x92\xae\x18\xbf\x9c\xef\x1e\xe7\xb1'

# Login

@router_main.route("/")

@router_main.route("/login", methods=["GET", "POST"])
def login():
    return render_template("/dashboard/login.html")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('router_main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def no_cache_and_login_required(view):
    @login_required
    @wraps(view)
    def wrapped_view(**kwargs):
        response = make_response(view(**kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return wrapped_view

@router_main.route("/procesar_login", methods=["POST"])
def procesar_login():
    try:
        conexion = obtener_conexion()
        if not conexion:
            return jsonify({
                'logeo': False,
                'mensaje': 'El servicio se encuentra inactivo.'
            }), 500    
        username = request.json.get('username')
        password = request.json.get('password')
        usuario = controlador_usuario.obtener_usuario_con_tipopersona_por_username(username)
        if usuario is None:
            return jsonify({'mensaje': 'El usuario no existe', 'logeo': False})
        elif usuario[2] == "I":
            return jsonify({'mensaje': 'El usuario está inactivo', 'logeo': False})     
        try:
            password_almacenada = controlador_usuario.descifrar_contraseña(usuario[3])
        except Exception as e:
            return jsonify({'mensaje': f'Error al descifrar la contraseña: {str(e)}', 'logeo': False})  
        if password == password_almacenada:
            login_attempts[username] = {'attempts': 0, 'last_attempt_time': 0}
            persona = controlador_usuario.obtener_datos_usuario(usuario[0])
            nombre = persona[0].split()[0]
            apellido = persona[1].split()[0]
            foto = persona[2]
            id_persona = usuario[5]
            id_tipo_usuario = usuario[4]
            idUsuario = usuario[0]
            session['user_id'] = id_persona
            session.permanent = True
            return jsonify({
                'logeo': True,
                'nombre': nombre,
                'apellido': apellido,
                'foto': foto,
                'id_persona': id_persona,
                'id_tipo_usuario': id_tipo_usuario,
                'idUsuario' : idUsuario
            })
        else:
            if username not in login_attempts:
                login_attempts[username] = {'attempts': 0, 'last_attempt_time': 0}
            login_attempts[username]['attempts'] += 1
            login_attempts[username]['last_attempt_time'] = time.time()
            return jsonify({'mensaje': 'La contraseña es incorrecta', 'logeo': False})
    except Exception as e:
        return jsonify({'mensaje': f'Error al procesar el login: {str(e)}', 'logeo': False})

@router_main.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('router_main.login'))

@router_main.route('/perfil')
@no_cache_and_login_required
def perfil():
    return render_template('/dashboard/perfil.html')

# Principal

@router_main.route("/index")
@no_cache_and_login_required
def index():
    return render_template("/dashboard/index.html")

@router_main.route("/indexga")
@no_cache_and_login_required
def gestion_academica():
    return render_template("gestion_academica/index.html")


@router_main.route("/indexppp")
@no_cache_and_login_required
def practicas_pre_profesionales():
    registros_por_fecha = obtener_estudiantes_por_fecha() or []
    estadisticas = obtener_estadisticas_estudiantes()
    ppp_finalizadas = obtener_ppp_finalizadas()
    return render_template("/ppp/index.html", registrosPorFecha=registros_por_fecha, estadisticas=estadisticas, ppp_finalizadas=ppp_finalizadas)

@router_main.route('/home')
@no_cache_and_login_required
def home():
    return render_template('home.html')

# Módulo de Gestión Académica

@router_main.route("/docente")
@no_cache_and_login_required
def docente():
    return render_template('/gestion_academica/docente.html')  

@router_main.route("/escuela")
@no_cache_and_login_required
def escuela():
    return render_template('/gestion_academica/escuela.html')

@router_main.route('/estudiante')
@no_cache_and_login_required
def estudiante():
    return render_template('/gestion_academica/estudiante.html')

@router_main.route('/jefe')
@no_cache_and_login_required
def jefe(): 
    return render_template('/gestion_academica/jefe.html')

@router_main.route("/facultad")
@no_cache_and_login_required
def facultad():
    return render_template('gestion_academica/facultad.html') 

@router_main.route("/genero")
@no_cache_and_login_required
def genero():
    return render_template('gestion_academica/genero.html') 

@router_main.route("/institucion")
@no_cache_and_login_required
def institucion():
    return render_template('gestion_academica/institucion.html') 

@router_main.route("/semestre")
@no_cache_and_login_required
def semestre():
    return render_template('gestion_academica/semestre.html')

@router_main.route("/usuario")
@no_cache_and_login_required
def usuario():
    return render_template('gestion_academica/usuario.html')

@router_main.route("/linea_desarrollo")
@no_cache_and_login_required
def linea_desarrollo():
    return render_template('gestion_academica/linea_desarrollo.html')

# Módulo de Prácticas Pre Profesionales

@router_main.route('/ppp_registro')
@no_cache_and_login_required
def ppp_registro():
    return render_template('ppp_registro.html')

@router_main.route("/InformeInicialEstudiante")
@no_cache_and_login_required
def informeInicialEstudiante():
    return render_template('ppp/informeInicialEstudiante.html') 

@router_main.route("/InformeInicialEmpresa")
@no_cache_and_login_required
def informeInicialEmpresa():
    return render_template('ppp/informeInicialEmpresa.html') 

@router_main.route("/InformeFinalEstudiante")
@no_cache_and_login_required
def informeFinalEstudiante():
    return render_template('ppp/informeFinalEstudiante.html') 

@router_main.route("/InformeFinalEmpresa")
@no_cache_and_login_required
def informeFinalEmpresa():
    return render_template('ppp/informeFinalEmpresa.html')

@router_main.route("/practicas")
@no_cache_and_login_required
def ppp():
    return render_template('ppp/ppp_registro.html')

@router_main.route("/InformesPorAlumno")
@no_cache_and_login_required
def InformesAlumno():
    return render_template('ppp/InformesAlumno.html')

@router_main.route("/horas-practica")
@no_cache_and_login_required
def horas_practica():
    return render_template('ppp/informeHorasPractica.html')

@router_main.route("/horas-practica-escuela")
@no_cache_and_login_required
def horas_practica_escuela():
    return render_template('ppp/informeHorasPracticaEscuela.html')

@router_main.route("/practicas-terminadas")
@no_cache_and_login_required
def practicas_terminadas():
    return render_template('ppp/informePracticasTerminadas.html')

@router_main.route("/dashboard-tendencias")
@no_cache_and_login_required
def dashboard_tendencias():
    return render_template('ppp/dashboardTendencias.html')

@router_main.route("/reporte_estudiantes_practicas")
@no_cache_and_login_required
def reporte_estudiantes_practicas():
    return render_template('gestion_academica/reportePracticas.html') 

# Funciones adicionales

@router_main.route("/datos_horas_practica")
def datos_horas_practica():
    try:
        datos = controlador_informeAlumno.obtener_reporte_horas_practicas()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@router_main.route("/datos_horas_practica_escuela")
def datos_horas_practica_escuela():
    try:
        datos = controlador_informeAlumno.obtener_resumen_horas_por_escuela()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
@router_main.route("/semestres")
def obtener_semestres():
    try:
        datos = controlador_informeAlumno.obtener_semestres()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router_main.route("/datos_practicas_terminadas")
def datos_practicas_terminadas():
    try:
        id_semestre = request.args.get('semestre', type=int)
        if not id_semestre:
            return jsonify({"error": "Semestre no especificado"}), 400
        
        datos = controlador_informeAlumno.obtener_practicas_terminadas_semestre(id_semestre)
        
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router_main.route("/datos_dashboard_tendencias")
def datos_dashboard_tendencias():
    try:
        datos = controlador_informeAlumno.obtener_dashboard_tendencias_escuela()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

@router_main.route("/escuelas")
def obtener_lista_escuelas():
    try:
        datos = controlador_informeAlumno.obtener_escuelas()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router_main.route("/instituciones_por_escuela")
def obtener_instituciones_escuela():
    try:
        id_escuela = request.args.get('escuela', type=int)
        if not id_escuela:
            return jsonify({"error": "Escuela no especificada"}), 400
        
        datos = controlador_informeAlumno.obtener_instituciones_por_escuela(id_escuela)
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500