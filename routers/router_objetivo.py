from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_objetivo as controlador_objetivo

router_objetivo = Blueprint('router_objetivo', __name__)

@router_objetivo.route('/datos_objetivo', methods=['GET'])
def datos_objetivo(): 
    objetivo = controlador_objetivo.obtener_objetivos()
    return jsonify(objetivo)

@router_objetivo.route("/agregar_objetivo", methods=["POST"])
def agregar_objetivo(): 
    descripcion = request.json.get('descripcion')
    idInforme = request.json.get('idInforme')
    resultado = controlador_objetivo.agregar_objetivos(descripcion, idInforme)
    return jsonify(resultado)