from flask import Blueprint, jsonify
import controladores.controlador_linea_desarrollo as controlador_linea_desarrollo

router_linea_desarrollo = Blueprint('router_linea_desarrollo', __name__)

# Ruta para obtener la lista de semestres
@router_linea_desarrollo.route("/datos_lineas_desarrollo", methods=["GET"])
def datos_lineas_desarrollo():
    lineas_desarrollo = controlador_linea_desarrollo.obtener_lineas_desarrollo()
    return jsonify(lineas_desarrollo)
