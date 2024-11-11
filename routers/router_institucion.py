from flask import Blueprint, jsonify, request
import controladores.controlador_institucion as controlador_institucion

router_institucion = Blueprint('router_institucion', __name__)

# Ruta para obtener la lista de instituciones
@router_institucion.route("/datos_instituciones", methods=["GET"])
def datos_instituciones():
    instituciones = controlador_institucion.obtener_instituciones()
    return jsonify(instituciones)

@router_institucion.route("/jefe_institucion", methods=["GET"])
def jefe_institucion():
    ruc = request.args.get('ruc')
    jefes = controlador_institucion.obtener_jefe(ruc)
    return jsonify(jefes)

@router_institucion.route("/obtener_institucion_por_numdoc/<string:numDoc>", methods=["GET"])
def obtener_institucion_por_numdoc(numDoc):
    institucion = controlador_institucion.obtener_institucion_por_numdoc(numDoc)
    return jsonify(institucion)

# Ruta para agregar una nueva institución
@router_institucion.route("/institucion", methods=["POST"])
def agregar_institucion():
    datos = request.get_json()
    numDoc = datos.get('numDoc')
    razonSocial = datos.get('razonSocial')
    direccion = datos.get('direccion')
    tel = datos.get('tel')
    correo = datos.get('correo')
    idDistrito = datos.get('idDistrito')
    idPersona = datos.get('idPersona')
    idTipoDoc = datos.get('idTipoDoc')

    resultado = controlador_institucion.agregar_institucion(
        numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc
    )
    return jsonify(resultado)

# Ruta para modificar una institución existente
@router_institucion.route("/institucion/<string:numDoc>", methods=["PUT"])
def modificar_institucion(numDoc):
    datos = request.get_json()
    razonSocial = datos.get('razonSocial')
    direccion = datos.get('direccion')
    tel = datos.get('tel')
    correo = datos.get('correo')
    idDistrito = datos.get('idDistrito')
    idPersona = datos.get('idPersona')
    idTipoDoc = datos.get('idTipoDoc')

    resultado = controlador_institucion.modificar_institucion(
        numDoc, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc
    )
    return jsonify(resultado)

# Ruta para eliminar una institución
@router_institucion.route("/institucion/<string:numDoc>", methods=["DELETE"])
def eliminar_institucion(numDoc):
    resultado = controlador_institucion.eliminar_institucion(numDoc)
    return jsonify(resultado)

# Ruta para dar de baja una institución (cambiar su estado a inactivo)
@router_institucion.route("/institucion/dar_baja/<string:numDoc>", methods=["PUT"])
def dar_de_baja_institucion(numDoc):
    resultado = controlador_institucion.dar_de_baja_institucion(numDoc)
    return jsonify(resultado)