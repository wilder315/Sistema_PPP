from flask import Blueprint, jsonify, request, render_template
from controladores.controlador_ficha_evaluacion import ControladorFichaEvaluacion, allowed_file

router_ficha_evaluacion = Blueprint('router_ficha_evaluacion', __name__)

@router_ficha_evaluacion.route('/ficha_evaluacion')
def ficha_evaluacion():
    return render_template('ppp/ficha_evaluacion.html')

@router_ficha_evaluacion.route('/api/estudiante/buscar')
def buscar_estudiante():
    try:
        nombre_estudiante = request.args.get('nombre', '')
        id_estudiante = request.args.get('id', '')
        modo = request.args.get('modo', 'busqueda')
        
        if modo == 'busqueda':
            if len(nombre_estudiante) < 3:
                return jsonify({"estudiantes": []}), 200
            datos = ControladorFichaEvaluacion.obtener_datos_estudiante(nombre_estudiante, modo)
        else:  # modo selección
            datos = ControladorFichaEvaluacion.obtener_datos_estudiante(id_estudiante, modo)
        
        if datos.get("error"):
            return jsonify(datos), 404
            
        return jsonify(datos), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router_ficha_evaluacion.route('/api/ficha_evaluacion', methods=['POST'])
def guardar_ficha():
    """Guarda una nueva ficha de evaluación"""
    firma = request.files.get('firma')
    datos_ficha = request.form.to_dict() 
    
    # Validar que todos los campos requeridos estén presentes
    campos_requeridos = [
        'idPractica', 'nombres_estudiante', 'escuela_profesional', 
        'periodo_practicas', 'area_desempeno', 'nombre_empresa',
        'direccion_empresa', 'nombre_responsable', 'correo_responsable',
        # Características evaluadas (todas son requeridas)
        'responsabilidad', 'proactividad', 'comunicacion_asertiva',
        'trabajo_equipo', 'compromiso_calidad', 'organizacion_trabajo',
        'puntualidad_asistencia',
        # Al menos un resultado de aprendizaje es requerido
        'resultado1', 'calificacion_resultado1',
        # Conclusiones son requeridas
        'conclusiones'
    ]
    
    for campo in campos_requeridos:
        if campo not in datos_ficha:
            return jsonify({
                "error": f"El campo {campo} es requerido"
            }), 400

    # Validar que las calificaciones tengan valores válidos
    calificaciones_validas = ['D', 'R', 'B', 'M']
    campos_calificacion = [
        'responsabilidad', 'proactividad', 'comunicacion_asertiva',
        'trabajo_equipo', 'compromiso_calidad', 'organizacion_trabajo',
        'puntualidad_asistencia', 'calificacion_resultado1'
    ]
    
    for campo in campos_calificacion:
        if campo in datos_ficha and datos_ficha[campo] not in calificaciones_validas:
            return jsonify({
                "error": f"La calificación para {campo} debe ser D, R, B o M"
            }), 400

    # Validar la firma
        if not firma:
            return jsonify({"error": "La firma es requerida"}), 400

        if not allowed_file(firma.filename):
                return jsonify({"error": "Formato de archivo no permitido"}), 400


    # Validar que si hay un resultado, debe tener calificación y viceversa
    for i in range(2, 11):  # Del resultado 2 al 10 (el 1 es obligatorio)
        resultado_key = f'resultado{i}'
        calificacion_key = f'calificacion_resultado{i}'
        
        if resultado_key in datos_ficha and not calificacion_key in datos_ficha:
            return jsonify({
                "error": f"Falta la calificación para el resultado de aprendizaje {i}"
            }), 400
        
        if calificacion_key in datos_ficha and not resultado_key in datos_ficha:
            return jsonify({
                "error": f"Falta la descripción para el resultado de aprendizaje {i}"
            }), 400
        
        if calificacion_key in datos_ficha and datos_ficha[calificacion_key] not in calificaciones_validas:
            return jsonify({
                "error": f"La calificación para el resultado {i} debe ser D, R, B o M"
            }), 400

    resultado = ControladorFichaEvaluacion.guardar_ficha_evaluacion(datos_ficha, firma)
    
    if resultado.get("error"):
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@router_ficha_evaluacion.route('/api/ficha_evaluacion', methods=['GET'])
def obtener_fichas():
    """Obtiene las fichas de evaluación"""
    id_practica = request.args.get('id_practica')
    
    fichas = ControladorFichaEvaluacion.obtener_fichas_evaluacion(id_practica)
    
    if isinstance(fichas, dict) and fichas.get("error"):
        return jsonify(fichas), 400
    return jsonify(fichas), 200


@router_ficha_evaluacion.route('/lista_fichas_evaluacion')
def listar_fichas_evaluacion():
    return render_template('ppp/lista_fichas_evaluacion.html')

@router_ficha_evaluacion.route('/api/fichas_evaluacion')
def obtener_lista_fichas():
    try:
        fichas = ControladorFichaEvaluacion.obtener_fichas_evaluacion()
        if isinstance(fichas, dict) and fichas.get("error"):
            return jsonify(fichas), 400
        return jsonify({"data": fichas}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@router_ficha_evaluacion.route('/api/ficha_evaluacion/<int:id_ficha>')
def obtener_ficha(id_ficha):
    """API para obtener una ficha específica"""
    try:
        ficha = ControladorFichaEvaluacion.obtener_ficha_por_id(id_ficha)
        if isinstance(ficha, dict) and ficha.get("error"):
            return jsonify(ficha), 404
        return jsonify(ficha), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router_ficha_evaluacion.route('/api/ficha_evaluacion/<int:id_ficha>', methods=['PUT'])
def actualizar_ficha(id_ficha):
    """API para actualizar una ficha existente"""
    try:
        # Obtener la firma si se envió
        firma = request.files.get('firma')
        
        # Obtener los datos del formulario
        datos = request.form.to_dict()
        
        # Validar calificaciones
        calificaciones_validas = {'D', 'R', 'B', 'M'}
        for i in range(1, 11):
            calificacion_key = f'calificacion_resultado{i}'
            resultado_key = f'resultado{i}'
            
            # Solo validar si existe la calificación y no está vacía
            if calificacion_key in datos and datos[calificacion_key]:
                if datos[calificacion_key] not in calificaciones_validas:
                    return jsonify({
                        "error": f"La calificación para el resultado {i} debe ser D, R, B o M"
                    }), 400
                
                # Si hay calificación, debe haber resultado
                if not datos.get(resultado_key):
                    return jsonify({
                        "error": f"Debe ingresar el resultado {i} si tiene calificación"
                    }), 400

            # Si hay resultado, debe haber calificación
            if resultado_key in datos and datos[resultado_key]:
                if not datos.get(calificacion_key):
                    return jsonify({
                        "error": f"Debe seleccionar una calificación para el resultado {i}"
                    }), 400

        # Actualizar la ficha
        resultado = ControladorFichaEvaluacion.actualizar_ficha(id_ficha, datos, firma)
        
        if resultado.get("error"):
            return jsonify(resultado), 400
            
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500