from flask import Blueprint, request, jsonify, render_template
from controladores.controlador_email import ControladorEmail

router_email = Blueprint('router_email', __name__)
controlador = ControladorEmail()

# Ruta para mostrar la interfaz de envío masivo
@router_email.route('/email/masivo', methods=['GET'])
def mostrar_formulario_masivo():
    """Muestra la interfaz para envío masivo de correos"""
    return render_template('emails/envio_masivo.html')

# Ruta API para envío automático de bienvenida
@router_email.route('/api/email/bienvenida/<int:id_persona>', methods=['POST'])
def enviar_correo_bienvenida(id_persona):
    """API para enviar correo de bienvenida automático"""
    try:
        resultado = controlador.enviar_correo_bienvenida_automatico(id_persona)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al enviar correo de bienvenida: {str(e)}"
        }), 500

# Ruta API para envío masivo
@router_email.route('/api/email/masivo', methods=['POST'])
def enviar_correo_masivo():
    """API para enviar correos masivos"""
    try:
        data = request.get_json()
        asunto = data.get('asunto', '')
        contenido = data.get('contenido', '')

        if not asunto or not contenido:
            return jsonify({
                "success": False,
                "message": "El asunto y contenido son requeridos"
            }), 400

        resultado = controlador.enviar_correo_masivo(asunto=asunto, contenido=contenido)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error al enviar correo masivo: {str(e)}"
        }), 500