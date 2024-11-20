from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_semestre as controlador_semestre


router_semestre = Blueprint('router_semestre', __name__)

@router_semestre.route("/semestre")
def semestre():
    return render_template('gestion_academica/semestre.html')

@router_semestre.route("/datos_semestres", methods=["GET"])
def datos_semestres():
    semestres = controlador_semestre.obtener_semestres()
    return jsonify(semestres)

@router_semestre.route("/datos_ultimos_semestres", methods=["GET"])
def datos_ultimos_semestres():
    semestres = controlador_semestre.obtener_ultimos_semestres()
    return jsonify(semestres)

@router_semestre.route("/obtener_semestre_por_id/<int:idSemestre>", methods=["GET"])
def obtener_semestre_por_id(idSemestre):
    semestres = controlador_semestre.obtener_semestre_por_id(idSemestre)
    return jsonify(semestres)

@router_semestre.route("/obtener_semestre_por_fecha/<string:fechaFin>", methods=["GET"])
def obtener_semestre_por_fecha(fechaFin):
    semestre = controlador_semestre.obtener_semestre_por_fecha(fechaFin)
    return jsonify(semestre)

@router_semestre.route("/agregar_semestre", methods=["POST"])
def agregar_semestre():
    nombre = request.json.get('nombre')
    fechaInicio = request.json.get('fechaInicio')
    fechaFin = request.json.get('fechaFin')
    estado = request.json.get('estado')
    resultado = controlador_semestre.agregar_semestre(nombre, fechaInicio, fechaFin, estado)
    return jsonify(resultado)

@router_semestre.route("/modificar_semestre", methods=["POST"])
def modificar_semestre():
    idsemestre = request.json.get('idSemestre')
    nombre = request.json.get('nombre')
    fechaInicio = request.json.get('fechaInicio')
    fechaFin = request.json.get('fechaFin')
    estado = request.json.get('estado')
    resultado = controlador_semestre.modificar_semestre(idsemestre, nombre, fechaInicio, fechaFin, estado)
    return jsonify(resultado)

@router_semestre.route("/dar_de_baja_semestre", methods=["POST"])
def dar_de_baja_semestre():
    idsemestre = request.json.get('idSemestre')
    resultado = controlador_semestre.dar_de_baja_semestre(idsemestre)
    return jsonify(resultado)

@router_semestre.route("/eliminar_semestre", methods=["POST"])
def eliminar_semestre():
    idsemestre = request.json.get('idSemestre')
    resultado = controlador_semestre.eliminar_semestre(idsemestre)
    return jsonify(resultado)

################################################## carlos delgado #################################################
@router_semestre.route('/dashboard2', methods=['POST'])
def dashboard2():
    data = request.json
    idEscuela = data.get('idEscuela', 0)
    idSemestre = data.get('idSemestre', 0)

    datos = controlador_semestre.obtener_datos_dashboard2(idEscuela, idSemestre)

    return jsonify(datos)

@router_semestre.route('/ultimos_estudiantes', methods=['POST'])
def ultimos_estudiantes():
    data = request.json
    idEscuela = data.get('idEscuela', 0)
    idSemestre = data.get('idSemestre', 0)

    # Obtener los últimos estudiantes registrados
    estudiantes = controlador_semestre.obtener_ultimos_estudiantes(idEscuela, idSemestre)
    
    return jsonify({'data': estudiantes})

@router_semestre.route('/estudiantes_por_institucion', methods=['POST'])
def estudiantes_por_institucion():
    data = request.json
    idEscuela = data.get('idEscuela', 0)
    idSemestre = data.get('idSemestre', 0)

    # Obtener los datos de estudiantes por institución
    instituciones = controlador_semestre.obtener_estudiantes_por_institucion(idEscuela, idSemestre)
    
    return jsonify({'data': instituciones})



