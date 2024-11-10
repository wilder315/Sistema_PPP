from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_estudiante as controlador_estudiante

router_estudiante = Blueprint('router_estudiante', __name__)

@router_estudiante.route("/estudiante")
def estudiante():
    return render_template('gestion_academica/estudiante.html')

@router_estudiante.route("/datos_estudiantes", methods=["GET"])
def datos_estudiantes():
    estudiantes = controlador_estudiante.obtener_estudiantes()
    return render_template('gestion_academica/index.html', registrosPorFecha=estudiantes)

@router_estudiante.route("/estudiante_fechas", methods=["GET"])
def estudiante_fechas():
    registros_por_fecha = controlador_estudiante.obtener_estudiantes_por_fecha()
    
    #agregar una validación para asegurar de que no sea None
    if registros_por_fecha is None: 
        registros_por_fecha = []
    
    print("Datos de registros_por_fecha:", registros_por_fecha)  # Verifica el contenido en la consola
    return render_template("gestion_academica/index.html", registrosPorFecha=registros_por_fecha)

@router_estudiante.route("/obtener_estudiante_por_id/<int:idEstudiante>", methods=["GET"])
def obtener_estudiante_por_id(idEstudiante):
    estudiante = controlador_estudiante.obtener_estudiante_por_id(idEstudiante)
    return jsonify(estudiante)

@router_estudiante.route("/obtener_estudiante_por_id_modificar/<int:idEstudiante>", methods=["GET"])
def obtener_estudiante_por_id_modificar(idEstudiante):
    estudiante = controlador_estudiante.obtener_estudiante_por_id_modificar(idEstudiante)
    return jsonify(estudiante)

@router_estudiante.route("/agregar_estudiante", methods=["POST"])
def agregar_estudiante():
    data = request.json
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    codUniversitario = data.get('codUniversitario')
    tel1 = data.get('tel1')
    tel2 = data.get('tel2')
    correoP = data.get('correoP')
    correoUSAT = data.get('correoUSAT')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idUsuario = data.get('idUsuario')
    idEscuela = data.get('idEscuela')

    resultado = controlador_estudiante.agregar_estudiante(numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela)
    return jsonify(resultado)

@router_estudiante.route("/modificar_estudiante", methods=["POST"])
def modificar_estudiante():
    data = request.json
    idEstudiante = data.get('idPersona')
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    codUniversitario = data.get('codUniversitario')
    tel1 = data.get('tel1')
    tel2 = data.get('tel2')
    correoP = data.get('correoP')
    correoUSAT = data.get('correoUSAT')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idUsuario = data.get('idUsuario')
    idEscuela = data.get('idEscuela')

    resultado = controlador_estudiante.modificar_estudiante(idEstudiante, numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idUsuario, idEscuela)
    return jsonify(resultado)

@router_estudiante.route("/dar_de_baja_estudiante", methods=["POST"])
def dar_de_baja_estudiante():
    idEstudiante = request.json.get('idEstudiante')
    resultado = controlador_estudiante.dar_de_baja_estudiante(idEstudiante)
    return jsonify(resultado)

@router_estudiante.route("/eliminar_estudiante", methods=["POST"])
def eliminar_estudiante():
    idEstudiante = request.json.get('idEstudiante')
    resultado = controlador_estudiante.eliminar_estudiante(idEstudiante)
    return jsonify(resultado)
