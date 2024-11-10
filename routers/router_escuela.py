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

@router_escuela.route("/obtener_escuela_por_id/<int:idEscuela>", methods=["GET"])
def obtener_escuela_por_id(idEscuela):
    escuelas = controlador_escuela.obtener_escuela_por_id(idEscuela)
    return jsonify(escuelas)

@router_escuela.route("/agregar_escuela", methods=["POST"])
def agregar_escuela():
    nombre = request.json.get('nombre')
    abreviatura = request.json.get('abreviatura')
    estado = request.json.get('estado')
    idFacultad = request.json.get('idFacultad')
    hRequeridas = request.json.get('hRequeridas')
    resultado = controlador_escuela.agregar_escuela(nombre, abreviatura, estado, idFacultad, hRequeridas)
    return jsonify(resultado)

@router_escuela.route("/modificar_escuela", methods=["POST"])
def modificar_escuela():
    idEscuela = request.json.get('idEscuela')
    nombre = request.json.get('nombre')
    abreviatura = request.json.get('abreviatura')
    estado = request.json.get('estado')
    idFacultad = request.json.get('idFacultad')
    hRequeridas = request.json.get('hRequeridas')
    resultado = controlador_escuela.modificar_escuela(idEscuela, nombre, abreviatura, estado, idFacultad, hRequeridas)
    return jsonify(resultado)

@router_escuela.route("/dar_de_baja_escuela", methods=["POST"])
def dar_de_baja_escuela():
    idEscuela = request.json.get('idEscuela')
    resultado = controlador_escuela.dar_de_baja_escuela(idEscuela)
    return jsonify(resultado)

@router_escuela.route("/eliminar_escuela", methods=["POST"])
def eliminar_escuela():
    idEscuela = request.json.get('idEscuela')
    resultado = controlador_escuela.eliminar_escuela(idEscuela)
    return jsonify(resultado)



