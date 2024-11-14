from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_tipoInforme as controlador_tipoInforme

router_tipoInforme = Blueprint('router_tipoInforme', __name__)

@router_tipoInforme.route('/datos_tipoinforme', methods=['GET'])
def datos_tipoinforme(): 
    tipoinforme = controlador_tipoInforme.obtener_tipo_informe()
    return jsonify(tipoinforme)

