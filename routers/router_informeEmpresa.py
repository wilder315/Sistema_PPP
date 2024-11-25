from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_informeEmpresa as controlador_informeEmpresa
from werkzeug.utils import secure_filename
import os
import base64
import uuid
from io import BytesIO


router_informeEmpresa = Blueprint('router_informeEmpresa', __name__)

# Ruta para manejar la carga de la imagen
@router_informeEmpresa.route('/subir_firma', methods=['POST'])
def subir_firma():
    # Verificar si la solicitud contiene un archivo
    if 'firma_imagen' not in request.files:
        return jsonify({'error': 'No se ha seleccionado un archivo'}), 400

    file = request.files['firma_imagen']

    # Verificar si el archivo tiene un nombre
    if file.filename == '':
        return jsonify({'error': 'No se ha seleccionado un archivo'}), 400

    # Asegurarse de que el archivo sea una imagen
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return jsonify({'error': 'El archivo no es una imagen válida'}), 400

    # Guardar el archivo con el nombre original y extensión .png
    filename = secure_filename(file.filename)
    filename = os.path.splitext(filename)[0] + '.png'  # Asegurarse de que la extensión sea .png
    file_path = os.path.join('static', 'img', filename)
    
    # Guardar la imagen
    file.save(file_path)

    # Retornar el nombre de la imagen para mostrarlo en el campo de texto
    return jsonify({'success': True, 'nombre_imagen': filename})

@router_informeEmpresa.route('/guardar_informe_final_empresa', methods=["POST"])
def guardar_informe_final_empresa(): 
    try:
        # Obtener los datos del formulario
        data = request.json
        numDoc = data.get('numDoc')
        area_desarrollo = data.get('area_desarrollo')
        texto_responsabilidad = data.get('texto_responsabilidad')
        texto_otros_aspectos = data.get('texto_otros_aspectos')
        firma_imagen_base64 = data.get('firma_imagen')
        cumplimiento_objetivos = data.get('cumplimiento_objetivos')
        fecha = data.get('fecha')
        
        # Convertir la imagen base64 a archivo
        if firma_imagen_base64:
            
            # Eliminar el prefijo de la cadena base64 (data:image/png;base64,...)
            if firma_imagen_base64.startswith('data:image'):
                header, base64_data = firma_imagen_base64.split(',', 1)
            else:
                base64_data = firma_imagen_base64

            # Decodificar la imagen base64
            img_data = base64.b64decode(base64_data)

            # Crear un nombre único para el archivo (usando UUID)
            unique_filename = str(uuid.uuid4()) + '.png'  # Puedes cambiar la extensión según el tipo de imagen
            file_path = os.path.join('static', 'img', unique_filename)

            # Guardar la imagen en la carpeta 'static/img/'
            with open(file_path, 'wb') as f:
                f.write(img_data)
        
        #llamar al controlador para agregar el informe
        resultado = controlador_informeEmpresa.guardar_informeFinalEmpresa(numDoc, area_desarrollo, texto_responsabilidad, texto_otros_aspectos, file_path, cumplimiento_objetivos, fecha)
        
        return jsonify(resultado) #retornar un mensaje de exito 
        
    except Exception as e: 
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500
