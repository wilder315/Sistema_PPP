from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_linea_desarrollo as controlador_linea_desarrollo

router_linea_desarrollo = Blueprint('router_linea_desarrollo', __name__)

@router_linea_desarrollo.route("/linea_desarrollo")
def linea_desarrollo():
    return render_template('gestion_academica/linea_desarrollo.html')


@router_linea_desarrollo.route("/datos_lineas_desarrollo", methods=["GET"])
def datos_lineas_desarrollo():
    lineas_desarrollo = controlador_linea_desarrollo.obtener_lineas_desarrollo()
    return jsonify(lineas_desarrollo)

@router_linea_desarrollo.route("/obtener_linea_desarrollo_por_id/<int:idLinea>", methods=["GET"])
def obtener_linea_desarrollo_por_id(idLinea):
    lineas_desarrollo = controlador_linea_desarrollo.obtener_linea_desarrollo_por_id(idLinea)
    return jsonify(lineas_desarrollo)

@router_linea_desarrollo.route("/agregar_linea_desarrollo", methods=["POST"])
def agregar_linea_desarrollo():
    nombre = request.json.get('nombre')
    estado = request.json.get('estado')
    idEscuela = request.json.get('idEscuela')
    resultado = controlador_linea_desarrollo.agregar_linea_desarrollo(nombre, estado, idEscuela)
    return jsonify(resultado)

@router_linea_desarrollo.route("/modificar_linea_desarrollo", methods=["POST"])
def modificar_linea_desarrollo():
    idLinea = request.json.get('idLinea')
    nombre = request.json.get('nombre')
    estado = request.json.get('estado')
    idEscuela = request.json.get('idEscuela')
    resultado = controlador_linea_desarrollo.modificar_linea_desarrollo(idLinea, nombre, estado, idEscuela)
    return jsonify(resultado)

@router_linea_desarrollo.route("/dar_de_baja_linea_desarrollo", methods=["POST"])
def dar_de_baja_linea_desarrollo():
    idLinea = request.json.get('idLinea')
    resultado = controlador_linea_desarrollo.dar_de_baja_linea_desarrollo(idLinea)
    return jsonify(resultado)

@router_linea_desarrollo.route("/eliminar_linea_desarrollo", methods=["POST"])
def eliminar_linea_desarrollo():
    idLinea = request.json.get('idLinea')
    resultado = controlador_linea_desarrollo.eliminar_linea_desarrollo(idLinea)
    return jsonify(resultado)
