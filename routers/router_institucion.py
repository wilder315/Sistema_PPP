from flask import Blueprint, jsonify, request
import controladores.controlador_institucion as controlador_institucion

router_institucion = Blueprint('router_institucion', __name__)

@router_institucion.route("/datos_instituciones", methods=["GET"])
def datos_instituciones():
    instituciones = controlador_institucion.obtener_instituciones()
    return jsonify(instituciones)

@router_institucion.route("/jefe_institucion", methods=["GET"])
def jefe_institucion():
    ruc = request.args.get('ruc')
    jefes = controlador_institucion.obtener_jefe(ruc)
    return jsonify(jefes)

@router_institucion.route("/datos_jefes", methods=["GET"])
def datos_jefes():
    jefes = controlador_institucion.obtener_jefes()
    return jsonify(jefes)

@router_institucion.route("/datos_paises", methods=["GET"])
def datos_paises():
    paises = controlador_institucion.obtener_paises()
    return jsonify(paises)

@router_institucion.route("/datos_departamentos", methods=["GET"])
def datos_departamentos():
    departamentos = controlador_institucion.obtener_departamentos()
    return jsonify(departamentos)

@router_institucion.route("/datos_provincias", methods=["GET"])
def datos_provincias():
    provincias = controlador_institucion.obtener_provincias()
    return jsonify(provincias)

@router_institucion.route("/datos_distritos", methods=["GET"])
def datos_distritos():
    distritos = controlador_institucion.obtener_distritos()
    return jsonify(distritos)

@router_institucion.route("/obtener_institucion_por_numdoc/<string:numDoc>", methods=["GET"])
def obtener_institucion_por_numdoc(numDoc):
    institucion = controlador_institucion.obtener_institucion_por_numdoc(numDoc)
    return jsonify(institucion)

@router_institucion.route("/agregar_institucion", methods=["POST"])
def agregar_institucion():
    datos = request.get_json()
    numDoc = datos.get('numDoc')
    giro = datos.get('giro')
    razonSocial = datos.get('razonSocial')
    direccion = datos.get('direccion')
    correo = datos.get('correo')
    tel = datos.get('tel')
    idDistrito = datos.get('idDistrito')
    idPersona = datos.get('idPersona')
    idTipoDoc = 3
    resultado = controlador_institucion.agregar_institucion(
        numDoc, giro, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc
    )
    return jsonify(resultado)

@router_institucion.route("/modificar_institucion", methods=["POST"])
def modificar_institucion():
    datos = request.get_json()
    numDoc = datos.get('numDoc')
    giro = datos.get('giro')
    razonSocial = datos.get('razonSocial')
    direccion = datos.get('direccion')
    correo = datos.get('correo')
    tel = datos.get('tel')
    idDistrito = datos.get('idDistrito')
    idPersona = datos.get('idPersona')
    idTipoDoc = 3
    resultado = controlador_institucion.modificar_institucion(
        numDoc, giro, razonSocial, direccion, tel, correo, idDistrito, idPersona, idTipoDoc
    )
    return jsonify(resultado)

@router_institucion.route("/eliminar_institucion", methods=["POST"])
def eliminar_facultad():
    numDoc = request.json.get('numDoc')
    resultado = controlador_institucion.eliminar_institucion(numDoc)
    return jsonify(resultado)