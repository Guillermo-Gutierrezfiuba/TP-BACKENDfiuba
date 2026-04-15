from flask import Blueprint, request, jsonify

from database.db import obtener_conexion

usuarios_blueprint = Blueprint('usuarios', __name__)

@usuarios_blueprint.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json

    if not all(datos in data for datos in("nombre",)):
        return jsonify({"error": "Faltan datos"}), 400
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(""" INSERT INTO usuarios(nombre)  VALUES (%s)""", (data['nombre'], ))
        conexion.commit()
    except:
        cursor.close()
        conexion.close()
        return jsonify({"error": "Usuario ya existe"}), 400
    
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Usuario creado"}), 201


@usuarios_blueprint.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(usuarios)

@usuarios_blueprint.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    conexion.close()
    cursor.close()


    if not usuario:
        return jsonify({"error": "No encontrado"}), 404


    return jsonify(usuario)

@usuarios_blueprint.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conexion = obtener_conexion
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Usuario eliminado"}), 201
    