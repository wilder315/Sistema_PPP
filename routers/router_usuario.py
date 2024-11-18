from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_usuario as controlador_usuario

router_usuario = Blueprint('router_usuario', __name__)

@router_usuario.route("/usuario")
def usuario():
    return render_template('gestion_academica/usuario.html')

@router_usuario.route("/datos_usuarios", methods=["GET"])
def datos_usuarios():
    usuarios = controlador_usuario.obtener_usuarios()
    return jsonify(usuarios)

@router_usuario.route("/datos_tipoUsuarios", methods=["GET"])
def datos_tipoUsuarios():
    tipo_usuarios = controlador_usuario.obtener_tipoUsuarios()
    return jsonify(tipo_usuarios)

@router_usuario.route("/obtener_usuario_por_id/<int:idUsuario>", methods=["GET"])
def obtener_usuario_por_id(idUsuario):
    usuarios = controlador_usuario.obtener_usuario_por_id(idUsuario)
    return jsonify(usuarios)

@router_usuario.route("/obtener_informacion_completa_persona/<int:idPersona>", methods=["GET"])
def obtener_informacion_completa_persona(idPersona):
    informacion = controlador_usuario.obtener_informacion_completa_persona(idPersona)
    return jsonify(informacion)

@router_usuario.route("/agregar_usuario", methods=["POST"])
def agregar_usuario():
    username = request.json.get('username')
    estado = request.json.get('estado')
    idTipoUsuario = request.json.get('idTipoUsuario')
    resultado = controlador_usuario.agregar_usuario(username, estado, idTipoUsuario)
    return jsonify(resultado)

@router_usuario.route("/actualizar_contraseña", methods=["POST"])
def actualizar_contraseña():
    id_usuario = request.json.get('idUsuario')
    nueva_password = request.json.get('nuevaPassword')
    resultado = controlador_usuario.actualizar_contraseña(id_usuario, nueva_password)
    return jsonify(resultado)

@router_usuario.route("/validar_contraseña_actual", methods=["POST"])
def validar_contraseña_actual():
    id_usuario = request.json.get('idUsuario')
    contraseña_actual = request.json.get('contraseñaActual')

    if not id_usuario or not contraseña_actual:
        return jsonify({"error": "ID de usuario y contraseña actual son requeridos"}), 400

    usuario = controlador_usuario.obtener_usuario_por_id(id_usuario)
    if usuario is None:
        return jsonify({"error": "Usuario no encontrado."}), 404

    try:
        password_almacenada = controlador_usuario.descifrar_contraseña(usuario['password'])
        if contraseña_actual == password_almacenada:
            return jsonify({"valida": True})
        else:
            return jsonify({"valida": False})
    except Exception as e:
        return jsonify({"error": f"Error al validar la contraseña: {str(e)}"}), 500

@router_usuario.route("/modificar_usuario", methods=["POST"])
def modificar_usuario():
    idUsuario = request.json.get('idUsuario')
    username = request.json.get('username')
    estado = request.json.get('estado')
    idTipoUsuario = request.json.get('idTipoUsuario')
    resultado = controlador_usuario.modificar_usuario(idUsuario, username, estado, idTipoUsuario)
    return jsonify(resultado)

@router_usuario.route("/dar_de_baja_usuario", methods=["POST"])
def dar_de_baja_usuario():
    idUsuario = request.json.get('idUsuario')
    resultado = controlador_usuario.dar_de_baja_usuario(idUsuario)
    return jsonify(resultado)

@router_usuario.route("/eliminar_usuario", methods=["POST"])
def eliminar_usuario():
    idUsuario = request.json.get('idUsuario')
    resultado = controlador_usuario.eliminar_usuario(idUsuario)
    return jsonify(resultado)

@router_usuario.route("/datos_usuarios_estudiantes", methods=["GET"])
def datos_usuarios_estudiantes():
    usuarios = controlador_usuario.obtener_usuarios_estudiantes()
    return jsonify(usuarios)

@router_usuario.route("/datos_usuarios_jefe", methods=["GET"])
def datos_usuarios_jefe(): 
    usuarios = controlador_usuario.obtener_usuarios_jefe()
    return jsonify(usuarios)

@router_usuario.route("/datos_usuarios_docentes", methods=["GET"])
def datos_usuarios_docentes():
    usuarios = controlador_usuario.obtener_usuarios_docentes()
    return jsonify(usuarios)

@router_usuario.route("/datos_usuario_informe", methods=["GET"])
def obtener_datos_usuario_informe():
    usuario_informe = controlador_usuario.obtener_datos_usuario_informe()
    return jsonify(usuario_informe)

@router_usuario.route('/descifrar_contraseña', methods=['POST'])
def descifrar_contraseña():
    try:
        data = request.json
        password_cifrada = data.get('passwordCifrada')
        if not password_cifrada:
            return jsonify({'error': 'No se proporcionó la contraseña cifrada.'})
        password_descifrada = controlador_usuario.descifrar_contraseña(password_cifrada)
        return jsonify({'password': password_descifrada})
    except Exception as e:
        return jsonify({'error': f'Error al descifrar la contraseña: {str(e)}'})
