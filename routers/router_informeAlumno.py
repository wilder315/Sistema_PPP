from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_informeAlumno as controlador_informeAlumno

router_informeAlumno = Blueprint('router_informeAlumno', __name__)

@router_informeAlumno.route("/informeAlumno")
def informeAlumno():
    return render_template('ppp/InformesAlumno.html')

@router_informeAlumno.route("/datos_informesAlumnos", methods=["GET"])
def datos_informesAlumnos():
    informesAlumnos = controlador_informeAlumno.obtener_informeAlumno()
    return jsonify(informesAlumnos)

@router_informeAlumno.route("/obtener_detalle_informe/<int:idInforme>", methods=["GET"])
def obtener_detalle_informe_route(idInforme):
    resultado = controlador_informeAlumno.obtener_detalle_informe(idInforme)
    return jsonify(resultado)

@router_informeAlumno.route("/aprobar_informe/<int:idInforme>", methods=["POST"])
def aprobar_informe(idInforme):
    try:
        resultado = controlador_informeAlumno.aprobar_informe(idInforme)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error al aprobar el informe: {str(e)}"})

@router_informeAlumno.route("/rechazar_informe/<int:idInforme>", methods=["POST"])
def rechazar_informe(idInforme):
    try:
        resultado = controlador_informeAlumno.rechazar_informe(idInforme)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error al rechazar el informe: {str(e)}"})