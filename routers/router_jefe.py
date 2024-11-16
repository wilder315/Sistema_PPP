from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_jefe as controlador_jefe

router_jefe = Blueprint('router_jefe', __name__)

@router_jefe.route("/jefe")
def jefe(): 
    return render_template("jefe.html")  

@router_jefe.route("/datoss_jefes", methods=["GET"])
def datoss_jefes(): 
    jefes = controlador_jefe.obtener_jefes()  # Llamamos al controlador
    return jsonify(jefes)  # Convertimos la respuesta a JSON

@router_jefe.route("/obtener_jefe_por_id/<int:idJefe>", methods=["GET"])
def obtener_jefe_por_id(idJefe):
    jefe = controlador_jefe.obtener_jefe_por_id(idJefe)   
    return jsonify(jefe)

@router_jefe.route("/obtener_jefe_por_id_modificar/<int:idJefe>", methods=["GET"])
def obtener_jefe_por_id_modificar(idJefe):
    jefe = controlador_jefe.obtener_jefe_por_id_modificar(idJefe)
    return jsonify(jefe)

@router_jefe.route("/agregar_jefe", methods=["POST"])
def agregar_jefe():
    data = request.json
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    tel1 = data.get('tel1')
    correoP = data.get('correoP')
    cargo = data.get('cargo')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idUsuario = 2  # Por ahora asumimos que el jefe tiene un usuario con id 2, en una implementación real, se debería obtener el id del usuario logueado.

    resultado = controlador_jefe.agregar_jefe(numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc, idUsuario)
    return jsonify(resultado)

@router_jefe.route("/modificar_jefe", methods=["POST"])
def modificar_jefe():
    data = request.json
    #idJefe = data.get('idJefe')
    numDoc = data.get('numDoc')
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    tel1 = data.get('tel1')
    correoP = data.get('correoP')
    cargo = data.get('cargo')
    estado = data.get('estado')
    idGenero = data.get('idGenero')
    idTipoDoc = data.get('idTipoDoc')
    idPersona = data.get('idPersona')

    resultado = controlador_jefe.modificar_jefe(numDoc, nombre, apellidos, tel1, correoP, cargo, estado, idGenero, idTipoDoc, idPersona)
    return jsonify(resultado)

@router_jefe.route("/eliminar_jefe", methods=["POST"])
def eliminar_jefe():
    idJefe = request.json.get('idJefe')
    resultado = controlador_jefe.eliminar_jefe(idJefe)
    return jsonify(resultado)

@router_jefe.route("/dar_de_baja_jefe", methods=["POST"])
def dar_de_baja_jefe():
    idJefe = request.json.get('idJefe')
    resultado = controlador_jefe.dar_de_baja_jefe(idJefe)
    return jsonify(resultado)