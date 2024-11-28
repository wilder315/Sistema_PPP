from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_estudiante as controlador_estudiante

router_estudiante = Blueprint('router_estudiante', __name__)

def cargar_foto():
    with open("static/img/fotoPerfil.txt", "r", encoding="utf-8") as file:
        foto = file.read()
    return foto

@router_estudiante.route("/estudiante")
def estudiante():
    return render_template('gestion_academica/estudiante.html')

@router_estudiante.route("/datos_estudiantes", methods=["GET"])
def datos_estudiantes():
    estudiantes = controlador_estudiante.obtener_estudiantes()
    return jsonify(estudiantes)

@router_estudiante.route("/datos_estudiantes_buscar", methods=["GET"])
def datos_estudiantes_buscar():
    estudiantes = controlador_estudiante.obtener_estudiantes_buscar()
    return jsonify(estudiantes)

@router_estudiante.route("/obtener_estudiante_por_id/<int:idEstudiante>", methods=["GET"])
def obtener_estudiante_por_id(idEstudiante):
    estudiante = controlador_estudiante.obtener_estudiante_por_id(idEstudiante)
    return jsonify(estudiante)

@router_estudiante.route("/obterner_ultima_practica_por_alumno/<int:idPersona>", methods=["GET"])
def obterner_ultima_practica_por_alumno(idPersona):
    estudiante = controlador_estudiante.obtener_ultima_practica_por_alumno(idPersona)
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
    foto = cargar_foto()
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idUsuario = data.get('idUsuario')
    idEscuela = data.get('idEscuela')

    resultado = controlador_estudiante.agregar_estudiante(numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, foto, estado, idGenero, idTipoDoc, idUsuario, idEscuela)
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
    idEscuela = data.get('idEscuela')

    resultado = controlador_estudiante.modificar_estudiante(idEstudiante, numDoc, nombre, apellidos, codUniversitario, tel1, tel2, correoP, correoUSAT, estado, idGenero, idTipoDoc, idEscuela)
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


@router_estudiante.route("/reporte_estudiantes_genero")
def reporte_estudiantes_genero():
    return render_template('gestion_academica/reporteEstudiantesGenero.html')

@router_estudiante.route("/datos_estudiantes_genero", methods=["GET"])
def datos_estudiantes_genero():
    datos = controlador_estudiante.obtener_estudiantes_por_genero_escuela()
    return jsonify(datos)


@router_estudiante.route("/reporte_estudiantes_semestre")
def reporte_estudiantes_semestre():
    return render_template('gestion_academica/reporteEstudiantesSemestre.html')

@router_estudiante.route("/datos_estudiantes_semestre", methods=["GET"])
def datos_estudiantes_semestre():
    datos = controlador_estudiante.obtener_estudiantes_por_semestre()
    return jsonify(datos)

@router_estudiante.route("/obtener_estudiante_por_doc/<string:doc_estudiante>", methods=["GET"])
def obtener_estudiante_por_doc(doc_estudiante):
    estudiante = controlador_estudiante.obtener_estudiante_por_doc(doc_estudiante)
    return jsonify(estudiante)

@router_estudiante.route('/dashboard', methods=['POST'])
def dashboard(): 
    #data = request.json
    datos = controlador_estudiante.obtener_estadisticas_estudiantes()
    
    return jsonify(datos)

@router_estudiante.route('/obtener_ppp_finalizadas', methods=['POST'])
def obtener_ppp_finalizadas(): 
    datos = controlador_estudiante.obtener_ppp_finalizadas()
    return jsonify(datos)

@router_estudiante.route('/obtener_estudiantes_por_fecha', methods=['POST'])
def obtener_estudiantes_por_fecha():
    datos = controlador_estudiante.obtener_estudiantes_por_fecha()
    return jsonify(datos)