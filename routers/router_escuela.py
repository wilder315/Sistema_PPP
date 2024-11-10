from flask import Blueprint, jsonify, request, render_template
from bd import obtener_conexion
import controladores.controlador_escuela as controlador_escuela

router_escuela = Blueprint('router_escuela', __name__)

@router_escuela.route("/escuela")
def escuela():
    return render_template('gestion_academica/escuela.html')

@router_escuela.route("/datos_escuelas", methods=["GET"])
def datos_escuelas():
    escuelas = controlador_escuela.obtener_escuelas()
    return jsonify(escuelas)

@router_escuela.route('/actualizar_escuela', methods=['POST'])
def actualizar_escuela():
    try:
        # Recoger los datos del JSON recibido
        data = request.json
        print("Datos recibidos:", data)  # Log para verificar los datos recibidos

        # Desempaquetar los datos recibidos
        id_escuela = data.get('idEscuela')
        nombre = data.get('nombre')
        abreviatura = data.get('abreviatura')
        estado = data.get('estado')
        id_facultad = data.get('facultad')  # Verifica que coincide con el nombre en el frontend
        h_requeridas = data.get('hRequeridas')

        # Verificar que todos los datos necesarios están presentes
        if not all([id_escuela, nombre, abreviatura, estado, id_facultad, h_requeridas]):
            print("Error: Faltan datos necesarios para realizar la actualización.")
            return jsonify({"error": "Faltan datos necesarios para realizar la actualización."}), 400

        # Conectar a la base de datos
        conexion = obtener_conexion()
        if not conexion:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return jsonify({"error": "No se pudo establecer conexión con la base de datos."}), 500
        
        with conexion.cursor() as cursor:
            # Verificar si la escuela existe
            cursor.execute("SELECT COUNT(*) FROM escuela WHERE idEscuela = %s", (id_escuela,))
            if cursor.fetchone()[0] == 0:
                print(f"Error: No se encontró una escuela con id {id_escuela}.")
                return jsonify({"error": f"No se encontró una escuela con id {id_escuela}."}), 404
            
            # Realizar la actualización
            cursor.execute("""
                UPDATE escuela
                SET nombre = %s, abreviatura = %s, estado = %s, idFacultad = %s, hRequeridas = %s
                WHERE idEscuela = %s
            """, (nombre, abreviatura, estado, id_facultad, h_requeridas, id_escuela))

            # Confirmar la transacción
            conexion.commit()
            print("Escuela actualizada correctamente.")

        # Responder con éxito
        return jsonify({"success": True, "message": "Escuela actualizada correctamente"})
    
    except Exception as e:
        print("Error al actualizar la escuela:", e)
        return jsonify({"error": f"Hubo un problema al actualizar los datos de la escuela. Detalle: {str(e)}"}), 500

    finally:
        if 'conexion' in locals():
            conexion.close()
            print("Conexión cerrada.")

##########################
@router_escuela.route("/datos_facultades", methods=["GET"])
def datos_facultades():
    facultades = controlador_escuela.obtener_facultades()
    return jsonify(facultades)  

@router_escuela.route('/obtener_escuela_por_id/<int:idEscuela>', methods=['GET'])
def obtener_escuela_por_id(idEscuela):
    escuela = controlador_escuela.obtener_escuela_por_id(idEscuela)
    
    if "error" in escuela:
        return jsonify(escuela), 400
    
    return jsonify(escuela)

@router_escuela.route("/agregar_escuela", methods=["POST"])
def agregar_escuela():
    data = request.json
    print("Datos recibidos para agregar:", data)  # Log para verificar los datos recibidos en agregar
    nombre = data.get('nombre')
    abreviatura = data.get('abreviatura')
    estado = data.get('estado')
    idFacultad = data.get('facultad')
    hRequeridas = data.get('hRequeridas')

    resultado = controlador_escuela.agregar_escuela(nombre, abreviatura, estado, idFacultad, hRequeridas)
    return jsonify(resultado)

@router_escuela.route("/dar_de_baja_escuela", methods=["POST"])
def dar_de_baja_escuela():
    idEscuela = request.json.get('idEscuela')
    resultado = controlador_escuela.dar_de_baja_escuela(idEscuela)
    return jsonify(resultado)

@router_escuela.route("/eliminar_escuela", methods=["POST"])
def eliminar_escuela():
    idEscuela = request.json.get('idEscuela')
    if not idEscuela:
        return jsonify({"error": "El ID de la escuela es requerido."})

    resultado = controlador_escuela.eliminar_escuela(idEscuela)
    return jsonify(resultado)



