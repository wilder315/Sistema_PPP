from flask import Blueprint, render_template, request, jsonify, session
from controladores.controlador_informeInicialEstudiante import obtener_instituciones, agregar_informe_final_estudiante, agregar_informe_inicial, agregar_informe_inicial_empresa, agregar_informe_final_empresa
from controladores import controlador_ppp as controlador_ppp
from controladores import controlador_informeInicialEstudiante as controlador_informeInicialEstudiante

router_informe = Blueprint('router_informe', __name__)

# Ruta para mostrar el formulario de informe inicial
@router_informe.route('/informe_inicial')
def informe_inicial(idPractica):
    instituciones = obtener_instituciones()
    practicas = controlador_ppp.obtener_practicas
    return render_template('informe_inicial.html', instituciones=instituciones, practicas=practicas)

# Ruta para obtener datos del responsable de la institución
@router_informe.route('/get_institucion_responsable/<numDoc>', methods=['GET'])
def get_institucion_responsable(numDoc):
    from controladores.controlador_informeInicialEstudiante import obtener_responsable_institucion
    datos = obtener_responsable_institucion(numDoc)
    return jsonify(datos)

# Ruta para agregar el informe inicial
@router_informe.route('/agregar_informe', methods=['POST'])
def agregar_informe():
    try:
        idPractica = request.form.get('idPractica')
        if not idPractica:
            return jsonify({"success": False, "error": "El ID de la práctica no fue proporcionado."})

        objetivos = request.form.getlist('objetivo[]')

        # Obtener datos del plan de trabajo
        plan_trabajo = []
        semanas = request.form.getlist('semana[]')
        fechas_inicio = request.form.getlist('fecha_inicio[]')
        fechas_fin = request.form.getlist('fecha_fin[]')
        actividades = request.form.getlist('actividad[]')
        horas = request.form.getlist('horas[]')

        for i in range(len(semanas)):
            plan_trabajo.append({
                "semana": semanas[i],
                "fecha_inicio": fechas_inicio[i],
                "fecha_fin": fechas_fin[i],
                "actividad": actividades[i],
                "horas": horas[i]
            })

        resultado = agregar_informe_inicial(idPractica, objetivos, plan_trabajo)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@router_informe.route('/obtener_practicas_informe_inicial', methods=['GET'])
def obtener_practicas_ajax():
        # Llama a la función del controlador y obtiene los datos
        practicas_informe_inicial = controlador_informeInicialEstudiante.obtener_practicas_informe_inicial()
        return jsonify(practicas_informe_inicial)

@router_informe.route('/agregar_informe_inicial_empresa', methods=['POST'])
def agregar_informe_empresa():
    try:
        idPractica = request.form.get('idPractica')
        nombre_empresa = request.form.get('nombre_empresa')
        responsable = request.form.get('responsable')
        cargo_responsable = request.form.get('cargo_responsable')
        nombre_estudiante = request.form.get('nombre_estudiante')
        apellido_estudiante = request.form.get('apellido_estudiante')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        aceptacion = request.form.get('aceptacion')
        labores = request.form.getlist('labores[]')

        if not idPractica:
            return jsonify({"success": False, "error": "El ID de la práctica no fue proporcionado."})

        resultado = agregar_informe_inicial_empresa(
            idPractica, nombre_empresa, responsable, cargo_responsable,
            nombre_estudiante, apellido_estudiante, fecha_inicio, fecha_fin,
            aceptacion, labores
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@router_informe.route("/agregar_informe_final_estudiante", methods=["POST"])
def agregar_informe_final_estudiante_route():
    try:
        data = request.get_json()
        idPractica = data.get("idPractica")
        fecha_entrega = data.get("fecha_entrega")
        introduccion = data.get("introduccion")
        cantidad_trabajadores = data.get("cantidad_trabajadores")
        mision = data.get("mision")
        vision = data.get("vision")
        infraestructura_fisica = data.get("infraestructura_fisica")
        infraestructura_tecnologica = data.get("infraestructura_tecnologica")
        area_trabajo = data.get("area_trabajo")
        labores_realizadas = data.get("labores_realizadas")
        bibliografia = data.get("bibliografia")
        organigrama = data.get("organigrama")
        anexos = data.get("anexos")
        conclusiones = data.get("conclusiones", [])
        recomendaciones = data.get("recomendaciones", [])

        resultado = agregar_informe_final_estudiante(
            idPractica, fecha_entrega, introduccion, cantidad_trabajadores,
            mision, vision, infraestructura_fisica, infraestructura_tecnologica,
            organigrama, area_trabajo, labores_realizadas, conclusiones,
            recomendaciones, bibliografia, anexos
        )

        return jsonify(resultado)
    except Exception as e:
        print(f"Error en la ruta: {e}")
        return jsonify({"error": str(e)})
    
@router_informe.route("/obtener_informe_final_estudiante/<int:idEstudiante>/<int:idPractica>", methods=["GET"])
def obtener_informe_final_estudiante(idEstudiante, idPractica):
    resultado = controlador_informeInicialEstudiante.obtener_informe_final_estudiante(idEstudiante, idPractica)
    return jsonify(resultado)

@router_informe.route('/agregar_informe_final_empresa', methods=['POST'])
def agregar_informe_final_empresa():
    try:
        nombre_empresa = request.form.get('nombre_empresa')
        responsable = request.form.get('responsable')
        grado_responsable = request.form.get('grado_responsable')
        cargo_responsable = request.form.get('cargo_responsable')
        nombre_estudiante = request.form.get('nombre_estudiante')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        cumplimiento_objetivos = request.form.get('cumplimiento_objetivos')
        cumplimiento_horas = request.form.get('cumplimiento_horas')
        responsabilidad = request.form.get('responsabilidad')
        otros_aspectos = request.form.get('otros_aspectos')
        fecha_firma = request.form.get('fecha_firma')
        firma_responsable = request.form.get('firma_responsable')
        cargo_firma = request.form.get('cargo_firma')

        resultado = agregar_informe_final_empresa(
            nombre_empresa, responsable, grado_responsable, cargo_responsable,
            nombre_estudiante, fecha_inicio, fecha_fin, cumplimiento_objetivos,
            cumplimiento_horas, responsabilidad, otros_aspectos, fecha_firma,
            firma_responsable, cargo_firma
        )

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    
@router_informe.route("/estado_informe_final/<int:idEstudiante>", methods=["GET"])
def estado_informe_final(idEstudiante):
    resultado = controlador_informeInicialEstudiante.obtener_estado_informe_final_estudiante(idEstudiante)
    return jsonify(resultado)
