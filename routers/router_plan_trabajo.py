from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_plan_trabajo as controlador_plan_trabajo

router_plan_trabajo = Blueprint('router_plan_trabajo', __name__)

@router_plan_trabajo.route('/datos_plan_trabajo', methods=['GET'])
def datos_plan_trabajo(): 
    plan_trabajo = controlador_plan_trabajo.obtener_plan_trabajo()
    return jsonify(plan_trabajo)

@router_plan_trabajo.route("/agregar_plan_trabajo", methods=["POST"])
def agregar_plan_trabajo(): 
    semana = request.json.get('semana')
    fechaInicio = request.json.get('fechaInicio')
    fechaFin = request.json.get('fechaFin')
    actividades = request.json.get('actividades')
    horas = request.json.get('horas')
    idInforme = request.json.get('idInforme')
    resultado = controlador_plan_trabajo.agregar_plan_trabajo(semana, fechaInicio, fechaFin, actividades, horas, idInforme)
    return jsonify(resultado)