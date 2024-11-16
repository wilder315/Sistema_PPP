from flask import Blueprint, render_template, request, jsonify, session
from controladores.controlador_informeInicialEstudiante import obtener_instituciones, obtener_responsable_institucion, agregar_informe_inicial

router_informe = Blueprint('router_informe', __name__)

# Ruta para mostrar el formulario de informe inicial
@router_informe.route('/informe_inicial')
def informe_inicial():
    instituciones = obtener_instituciones()
    return render_template('informe_inicial.html', instituciones=instituciones)

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