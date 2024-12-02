from flask import Blueprint, jsonify, request, render_template, jsonify
import controladores.controlador_informeEmpresa as controlador_informeEmpresa
from werkzeug.utils import secure_filename
import os
import base64
import uuid
from io import BytesIO
import json



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
        data = request.json
        numDoc = data.get('numDoc')
        texto_responsabilidad = data.get('texto_responsabilidad')
        texto_otros_aspectos = data.get('texto_otros_aspectos')
        firma_imagen_base64 = data.get('firma_imagen')
        cumplimiento_objetivos = data.get('cumplimiento_objetivos')
        fecha = data.get('fecha')
        
        if firma_imagen_base64:
            if firma_imagen_base64.startswith('data:image'):
                header, base64_data = firma_imagen_base64.split(',', 1)
            else:
                base64_data = firma_imagen_base64

            img_data = base64.b64decode(base64_data)

            unique_filename = str(uuid.uuid4()) + '.png'  # Puedes cambiar la extensión según el tipo de imagen
            file_path = os.path.join('static', 'img', unique_filename)

            # Guardar la imagen en la carpeta 'static/img/'
            with open(file_path, 'wb') as f:
                f.write(img_data)
        
        #llamar al controlador para agregar el informe
        resultado = controlador_informeEmpresa.guardar_informeFinalEmpresa(numDoc, texto_responsabilidad, texto_otros_aspectos, file_path, cumplimiento_objetivos, fecha)
        
        return jsonify(resultado) #retornar un mensaje de exito 
        
    except Exception as e: 
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500


@router_informeEmpresa.route('/buscar_estudiantes', methods=['GET'])
def buscar_estudiantes():
    try:
        termino_busqueda = request.args.get('termino', '')
        if len(termino_busqueda) < 2:
            return jsonify([])
            
        estudiantes = controlador_informeEmpresa.buscar_estudiantes_practicas(termino_busqueda)
        return jsonify(estudiantes)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@router_informeEmpresa.route('/buscar_instituciones', methods=['GET'])
def buscar_instituciones():
    try:
        termino_busqueda = request.args.get('termino', '')
        if len(termino_busqueda) < 2:
            return jsonify([])
            
        instituciones = controlador_informeEmpresa.buscar_instituciones(termino_busqueda)
        return jsonify(instituciones)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
@router_informeEmpresa.route('/guardar_informe_inicial_empresa', methods=['POST'])
def guardar_informe_inicial_empresa():
    try:
        aceptacion = request.form.get('aceptacion')
        labor = request.form.get('labor')
        labores = request.form.get('labores')
        firma1 = request.files.get('firma1')
        firma2 = request.files.get('firma2')
        if not all([aceptacion, labor, labores, firma1, firma2]):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        resultado = controlador_informeEmpresa.guardar_informeInicialEmpresa(
            aceptacion,
            json.loads(labor),
            json.loads(labores),
            firma1,
            firma2
        )
        print(resultado)
        return jsonify(resultado)
    except Exception as e:
        print("Error en guardar_informe_inicial_empresa:", str(e))
        return jsonify({"error": str(e)}), 500  

@router_informeEmpresa.route('/actualizar_informe', methods=['POST'])
def actualizar_informe():
    try:
        id_informe = request.form.get('idInforme')
        fecha = request.form.get('fecha')
        aceptacion = request.form.get('aceptacion')
        labor = request.form.get('labor')  
        labores = request.form.get('labores')  
        firma1 = request.files.get('firma1')
        firma2 = request.files.get('firma2')

        resultado = controlador_informeEmpresa.actualizar_informe(
            id_informe,
            fecha,
            aceptacion,
            json.loads(labor),
            json.loads(labores),
            firma1,
            firma2
        )
        return jsonify(resultado)
    except Exception as e:
        print("Error en ruta actualizar_informe:", str(e))
        return jsonify({"error": str(e)}), 500
    
@router_informeEmpresa.route('/listar_informes_empresa', methods=['GET'])
def listar_informes_empresa():
    try:
        informes = controlador_informeEmpresa.obtener_informes_empresa()
        return jsonify(informes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@router_informeEmpresa.route('/obtener_informe/<int:id_informe>', methods=['GET'])
def obtener_informe(id_informe):
    try:
        informe = controlador_informeEmpresa.obtener_informe_por_id(id_informe)
        return jsonify(informe)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
