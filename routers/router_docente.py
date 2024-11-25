from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_docente as controlador_docente

router_docente = Blueprint('router_docente', __name__)

def cargar_foto():
    with open("static/img/fotoPerfil.txt", "r", encoding="utf-8") as file:
        foto = file.read()
    return foto

@router_docente.route("/docente")
def docente():
    return render_template('gestion_academica/docente.html')

@router_docente.route("/datos_docentes", methods=["GET"])
def datos_docentes():
    docentes = controlador_docente.obtener_docentes()
    return jsonify(docentes)

@router_docente.route("/obtener_docente_por_id/<int:idDocente>", methods=["GET"])
def obtener_docente_por_id(idDocente):
    docente = controlador_docente.obtener_docente_por_id(idDocente)
    return jsonify(docente)

@router_docente.route("/agregar_docente", methods=["POST"])
def agregar_docente():
    data = request.json
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    tel1 = data.get('tel1')
    tel2 = data.get('tel2')
    correoP = data.get('correoP')
    correoUSAT = data.get('correoUSAT')
    foto = cargar_foto()
    cargo = data.get('cargo')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idEscuela = data.get('idEscuela')

    resultado = controlador_docente.agregar_docente(numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, foto, cargo, estado, idGenero, idTipoDoc, idEscuela)
    return jsonify(resultado)

@router_docente.route("/modificar_docente", methods=["POST"])
def modificar_docente():
    data = request.json
    idDocente = data.get('idPersona')
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    tel1 = data.get('tel1')
    tel2 = data.get('tel2')
    correoP = data.get('correoP')
    correoUSAT = data.get('correoUSAT')
    cargo = data.get('cargo')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idEscuela = data.get('idEscuela')

    resultado = controlador_docente.modificar_docente(idDocente, numDoc, nombre, apellidos, tel1, tel2, correoP, correoUSAT, cargo, estado, idGenero, idTipoDoc, idEscuela)
    return jsonify(resultado)

@router_docente.route("/dar_de_baja_docente", methods=["POST"])
def dar_de_baja_docente():
    idDocente = request.json.get('idDocente')
    resultado = controlador_docente.dar_de_baja_docente(idDocente)
    return jsonify(resultado)

@router_docente.route("/eliminar_docente", methods=["POST"])
def eliminar_docente():
    idDocente = request.json.get('idDocente')
    resultado = controlador_docente.eliminar_docente(idDocente)
    return jsonify(resultado)