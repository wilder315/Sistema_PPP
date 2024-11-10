from flask import Blueprint, render_template, request, redirect, jsonify, make_response, session

import hashlib
import random
import os
from werkzeug.utils import secure_filename
from bd import obtener_conexion
from bd import obtener_conexion
import controladores.controlador_usuario as controlador_usuario
import controladores.controlador_informeAlumno as controlador_informeAlumno
import time

login_attempts = {}
router_main = Blueprint('router_main', __name__)

# Login

@router_main.route("/")
@router_main.route("/login", methods=["GET", "POST"])
def login():
    return render_template("/dashboard/login.html")

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
        if username not in login_attempts:
            login_attempts[username] = {'attempts': 0, 'last_attempt_time': 0}
        if login_attempts[username]['attempts'] >= 3 and (time.time() - login_attempts[username]['last_attempt_time']) < 300:
            return jsonify({'mensaje': 'Cuenta bloqueada. Intente de nuevo más tarde.', 'logeo': False})      
        if usuario is None:
            return jsonify({'mensaje': 'El usuario no existe', 'logeo': False})
        elif usuario[2] == "I":
            return jsonify({'mensaje': 'El usuario está inactivo', 'logeo': False})
        else:
            h = hashlib.new("sha256")
            h.update(bytes(password, encoding="utf-8"))
            encpassword = h.hexdigest()

            if encpassword == usuario[3]:
                login_attempts[username] = {'attempts': 0, 'last_attempt_time': 0}
                persona = controlador_usuario.obtener_datos_usuario(usuario[0])
                nombre = persona[0].split()[0]
                apellido = persona[1].split()[0]
                foto = persona[2]
                session['user_id'] = usuario[0]
                return jsonify({
                    'logeo': True,
                    'nombre': nombre,
                    'apellido': apellido,
                    'foto': foto
                })
            else:
                login_attempts[username]['attempts'] += 1
                login_attempts[username]['last_attempt_time'] = time.time()
                return jsonify({'mensaje': 'La contraseña es incorrecta', 'logeo': False})
    except Exception as e:
        return jsonify({'mensaje': f'Error al procesar el login: {str(e)}', 'logeo': False})

# Principal

@router_main.route("/index")
def index():
    return render_template("/dashboard/index.html")

@router_main.route("/indexga")
def gestion_academica():
    return render_template("/gestion_academica/index.html")

@router_main.route("/indexppp")
def practicas_pre_profesionales():
    return render_template("/ppp/index.html")

@router_main.route('/home')
def home():
    return render_template('home.html')

@router_main.route('/perfil')
def perfil():
    return render_template('perfil.html')

# Módulo de Gestión Académica

@router_main.route("/docente")
def docente():
    return render_template('/gestion_academica/docente.html')  

@router_main.route("/escuela")
def escuela():
    return render_template('/gestion_academica/escuela.html')

@router_main.route('/estudiante')
def estudiante():
    return render_template('/gestion_academica/estudiante.html')

@router_main.route("/facultad")
def facultad():
    return render_template('gestion_academica/facultad.html') 

@router_main.route("/genero")
def genero():
    return render_template('gestion_academica/genero.html') 

@router_main.route("/institucion")
def institucion():
    return render_template('gestion_academica/institucion.html') 

@router_main.route("/semestre")
def semestre():
    return render_template('gestion_academica/semestre.html')

@router_main.route("/usuario")
def usuario():
    return render_template('gestion_academica/usuario.html')

# Módulo de Prácticas Pre Profesionales

@router_main.route('/ppp_registro')
def ppp_registro():
    return render_template('ppp_registro.html')

@router_main.route("/InformeInicialEstudiante")
def informeInicialEstudiante():
    return render_template('ppp/informeInicialEstudiante.html') 

@router_main.route("/InformeInicialEmpresa")
def informeInicialEmpresa():
    return render_template('ppp/informeInicialEmpresa.html') 

@router_main.route("/InformeFinalEstudiante")
def informeFinalEstudiante():
    return render_template('ppp/informeFinalEstudiante.html') 

@router_main.route("/InformeFinalEmpresa")
def informeFinalEmpresa():
    return render_template('ppp/informeFinalEmpresa.html')

@router_main.route("/practicas")
def ppp():
    return render_template('ppp/ppp_registro.html')

@router_main.route("/InformesPorAlumno")
def InformesAlumno():
    return render_template('ppp/InformesAlumno.html')

@router_main.route("/horas-practica")
def horas_practica():
    return render_template('ppp/informeHorasPractica.html')

@router_main.route("/horas-practica-escuela")
def horas_practica_escuela():
    return render_template('ppp/informeHorasPracticaEscuela.html')



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
    
    
@router_main.route("/practicas-terminadas")
def practicas_terminadas():
    return render_template('ppp/informePracticasTerminadas.html')

@router_main.route("/datos_practicas_terminadas")
def datos_practicas_terminadas():
    try:
        # Obtener mes y año de los parámetros de la URL
        mes = request.args.get('mes', type=int)
        anio = request.args.get('anio', type=int)
        
        # Si no se proporcionan mes y año, usar los valores actuales
        if not mes or not anio:
            from datetime import datetime
            fecha_actual = datetime.now()
            mes = fecha_actual.month
            anio = fecha_actual.year
        
        # Llamar al controlador con los parámetros
        datos = controlador_informeAlumno.obtener_practicas_terminadas_mes(mes, anio)
        
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@router_main.route("/dashboard-tendencias")
def dashboard_tendencias():
    return render_template('ppp/dashboardTendencias.html')

@router_main.route("/datos_dashboard_tendencias")
def datos_dashboard_tendencias():
    try:
        datos = controlador_informeAlumno.obtener_dashboard_tendencias_escuela()
        if isinstance(datos, dict) and "error" in datos:
            return jsonify({"error": datos["error"]}), 500
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500    