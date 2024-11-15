from flask import Blueprint, jsonify
import controladores.controlador_tipoDocumento as controlador_tipoDocumento

router_tipoDocumento = Blueprint('router_tipoDocumento', __name__)

# Ruta para obtener la lista de géneros
@router_tipoDocumento.route("/datos_tipoDocumentos", methods=["GET"])
def datos_tipoDocumento():
    tipoDocumentos = controlador_tipoDocumento.obtener_tipoDocumento()
    return jsonify(tipoDocumentos)

@router_tipoDocumento.route("/datos_tipoDocumentosEstudiante", methods=["GET"])
def datos_tipoDocumentosEstudiante():
    tipoDocumentos = controlador_tipoDocumento.obtener_tipoDocumentoEstudiante()
    return jsonify(tipoDocumentos)