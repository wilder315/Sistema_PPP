from flask import Blueprint, jsonify, request, render_template
import controladores.controlador_ppp as controlador_practicas

router_practicas = Blueprint('router_practicas', __name__)

@router_practicas.route("/practicas")
def practicas():
    return render_template('ppp/ppp_registro.html')

@router_practicas.route("/datos_practicas", methods=["GET"])
def datos_practicas():
    practicas = controlador_practicas.obtener_practicas()
    return jsonify(practicas)

@router_practicas.route("/obtener_ultimo_id", methods=["GET"])
def obtener_ultimo_id():
    practicas = controlador_practicas.obtener_ultimo_id()
    return jsonify(practicas)

@router_practicas.route("/obtener_practica_por_id/<int:idPractica>", methods=["GET"])
def obtener_practica_por_id(idPractica):
    practica = controlador_practicas.obtener_practica_por_id(idPractica)
    return jsonify(practica)

@router_practicas.route("/obtener_practica_por_estudiante/<int:id_estudiante>", methods=["GET"])
def obtener_practica_por_estudiante(id_estudiante):
    practica = controlador_practicas.obtener_practica_por_estudiante(id_estudiante)
    return jsonify(practica)

@router_practicas.route("/informes_practica/<int:idPractica>", methods=["GET"])
def informes_practica(idPractica):
    informes = controlador_practicas.informes_practica(idPractica)
    return jsonify(informes)

@router_practicas.route("/agregar_practica", methods=["POST"])
def agregar_practica():
    data = request.json
    fechaInicio = data.get('fechaInicio')
    horario = data.get('horario')
    modalidad = data.get('modalidad')
    area = data.get('area')
    numeroHorasPPP = data.get('numeroHorasPPP')
    numeroHorasPendientes = data.get('numeroHorasPendientes')
    numeroHorasRealizadas = data.get('numeroHorasRealizadas')
    idSemestre = data.get('idSemestre')
    idLinea = data.get('idLinea')
    numDocInstitucion = data.get('numDocInstitucion')
    idTipoPractica = data.get('idTipoPractica')
    idPersona = data.get('idPersona')
    
    resultado = controlador_practicas.agregar_practica(fechaInicio, horario, modalidad, area, numeroHorasPPP, numeroHorasPendientes, numeroHorasRealizadas, idSemestre, idLinea, numDocInstitucion, idTipoPractica, idPersona)
    return jsonify(resultado)

@router_practicas.route("/modificar_practica", methods=["POST"])
def modificar_practica():
    data = request.json
    idPractica = data.get('idPractica')
    fechaInicio = data.get('fechaInicio')
    fechaFin = data.get('fechaFin')
    modalidad = data.get('modalidad')
    area = data.get('area')
    numeroHorasPPP = data.get('numeroHorasPPP')
    numDocEstudiante = data.get('numDocEstudiante')
    idSemestre = data.get('idSemestre')
    idLinea = data.get('idLinea')
    numDocInstitucion = data.get('numDocInstitucion')
    idEstado = data.get('idEstado')
    idTipoPractica = data.get('idTipoPractica')
    
    resultado = controlador_practicas.modificar_practica(idPractica, fechaInicio, fechaFin, modalidad, area, numeroHorasPPP, numDocEstudiante, idSemestre, idLinea, numDocInstitucion, idEstado, idTipoPractica)
    return jsonify(resultado)

@router_practicas.route("/eliminar_practica", methods=["POST"])
def eliminar_practica():
    idPractica = request.json.get('idPractica')
    resultado = controlador_practicas.eliminar_practica(idPractica)
    return jsonify(resultado)

@router_practicas.route("/cambiar_estado_practica", methods=["POST"])
def cambiar_estado_practica():
    idPractica = request.json.get('idPractica')
    nuevo_estado = request.json.get('nuevo_estado')
    resultado = controlador_practicas.cambiar_estado_practica(idPractica, nuevo_estado)
    return jsonify(resultado)

@router_practicas.route("/practicas_activas", methods=["GET"])
def practicas_activas():
    resultado = controlador_practicas.obtener_practicas_activas()
    return jsonify(resultado)

@router_practicas.route("/practicas_con_estado", methods=["GET"])
def practicas_con_estado():
    resultado = controlador_practicas.obtener_practicas_con_estado()
    return jsonify(resultado)

################################ Reportes Carlos Delgado ############################### 
@router_practicas.route("/reporte_practicas1", methods=["POST"])
def reporte_practicas1():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        #mostrar los datos que llegaron del backend para verificar 
        #print(data)

        # Obtener los parámetros con valores por defecto si no se envían
        idSemestre = data.get('idSemestre', 0)
        idEscuela = data.get('idEscuela', 0)
        idEstado = data.get('idEstado', 0)
        numDoc = data.get('numDoc', 0)

        # Llamar al controlador
        resultado = controlador_practicas.reporte_practicas_estudiantes(
            idSemestre, idEscuela, idEstado, numDoc
        )

        if not resultado:
            return jsonify({"message": "No se encontraron prácticas para los criterios dados"}), 404
        
        return jsonify({"data": resultado})  # Devolver los valores bajo la clave 'data'

    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500
    
@router_practicas.route("/reporte_horas_practica2", methods=["GET"])
def reporte_horas_practica2():
    # Obtener el parámetro `idPersona` de la solicitud
    cod_universitario = request.args.get('codUniversitario')  # Obtiene el parámetro como string
    
    # Llamar a la función con el codUniversitario si fue proporcionado
    reporte_horas = controlador_practicas.obtener_reporte_horas_practicas2(cod_universitario)
    
    # Retornar el resultado en formato JSON
    return jsonify(reporte_horas)