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
    
@router_informe.route('/agregar_informe_final_estudiante', methods=['POST'])
def agregar_informe_final():
    try:
        idPractica = request.form.get('idPractica')
        nombre_estudiante = request.form.get('nombre_estudiante')
        apellido_estudiante = request.form.get('apellido_estudiante')
        nombre_institucion = request.form.get('nombre_institucion')
        fecha_entrega = request.form.get('fecha_entrega')
        introduccion = request.form.get('introduccion')
        razon_social = request.form.get('razon_social')
        direccion = request.form.get('direccion')
        giro_institucion = request.form.get('giro_institucion')
        representante = request.form.get('representante')
        mision = request.form.get('mision')
        vision = request.form.get('vision')
        cantidad_trabajadores = request.form.get('cantidad_trabajadores')
        infraestructura_fisica = request.form.get('infraestructura_fisica')
        infraestructura_tecnologica = request.form.get('infraestructura_tecnologica')
        organigrama = request.form.get('organigrama')
        area_trabajo = request.form.get('area_trabajo')
        labores_realizadas = request.form.get('labores_realizadas')
        conclusiones = request.form.getlist('conclusiones[]')
        bibliografia = request.form.get('bibliografia')
        recomendaciones = request.form.getlist('recomendaciones[]')
        anexos = request.form.get('anexos')

        resultado = agregar_informe_final_estudiante(
            idPractica, nombre_estudiante, apellido_estudiante, nombre_institucion, fecha_entrega, introduccion,
            razon_social, direccion, giro_institucion, representante, mision, vision, cantidad_trabajadores,
            infraestructura_fisica, infraestructura_tecnologica, organigrama, area_trabajo, labores_realizadas,
            conclusiones, bibliografia, recomendaciones, anexos
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@router_informe.route('/agregar_informe_final_empresa', methods=['POST'])
def agregar_informe_final_empresa():
    try:
        # Obtener datos del formulario
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

        # Llamar al controlador para agregar el informe
        resultado = agregar_informe_final_empresa(
            nombre_empresa, responsable, grado_responsable, cargo_responsable,
            nombre_estudiante, fecha_inicio, fecha_fin, cumplimiento_objetivos,
            cumplimiento_horas, responsabilidad, otros_aspectos, fecha_firma,
            firma_responsable, cargo_firma
        )

        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})