from flask import Blueprint, request, jsonify, url_for
import mysql.connector
from db import obtener_conexion

usuarios_blueprint = Blueprint("usuarios", __name__)


def respuesta_error(codigo, mensaje, descripcion):
    return jsonify({
        "errors": [
            {
                "code": codigo,
                "message": mensaje,
                "level": "error",
                "description": descripcion
            }
        ]
    })


def leer_paginacion():
    limit = request.args.get("_limit", request.args.get("limit", 10), type=int)
    offset = request.args.get("_offset", request.args.get("offset", 0), type=int)

    if limit is None:
        limit = 10
    if offset is None:
        offset = 0

    if limit < 1 or offset < 0:
        return None, None

    return limit, offset


def construir_links(total, limit, offset):
    def armar_href(nuevo_offset):
        return url_for(
            "usuarios.listar_usuarios",
            _external=False,
            **{"_limit": limit, "_offset": nuevo_offset}
        )

    if total == 0:
        ultimo_offset = 0
    else:
        ultimo_offset = ((total - 1) // limit) * limit

    links = {
        "_first": {"href": armar_href(0)},
        "_prev": {"href": armar_href(max(offset - limit, 0))},
        "_next": {"href": armar_href(offset + limit)} if offset + limit < total else None,
        "_last": {"href": armar_href(ultimo_offset)}
    }

    return links


@usuarios_blueprint.route("/usuarios", methods=["POST"])
def crear_usuario():
    data = request.get_json(silent=True)

    if not data:
        return respuesta_error(
            "USR400",
            "Bad Request",
            "El body debe ser JSON válido."
        ), 400

    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return respuesta_error(
            "USR401",
            "Bad Request",
            "Los campos 'nombre' y 'email' son obligatorios."
        ), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
            (nombre, email)
        )
        conexion.commit()
        return "", 201

    except mysql.connector.Error as error:
        if error.errno == 1062:
            return respuesta_error(
                "USR409",
                "Conflict",
                "Ya existe un usuario con ese email."
            ), 409

        return respuesta_error(
            "USR500",
            "Internal Server Error",
            f"Error al crear el usuario: {error}"
        ), 500

    finally:
        cursor.close()
        conexion.close()


@usuarios_blueprint.route("/usuarios", methods=["GET"])
def listar_usuarios():
    limit, offset = leer_paginacion()

    if limit is None or offset is None:
        return respuesta_error(
            "USR402",
            "Bad Request",
            "Los parámetros de paginación son inválidos."
        ), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT id, nombre, email FROM usuarios ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset)
        )
        usuarios = cursor.fetchall()

        if not usuarios:
            return "", 204

        return jsonify({
            "usuarios": usuarios,
            "_links": construir_links(total, limit, offset)
        }), 200

    except mysql.connector.Error as error:
        return respuesta_error(
            "USR500",
            "Internal Server Error",
            f"Error al listar usuarios: {error}"
        ), 500

    finally:
        cursor.close()
        conexion.close()


@usuarios_blueprint.route("/usuarios/<int:id>", methods=["GET"])
def obtener_usuario(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT id, nombre, email FROM usuarios WHERE id = %s",
            (id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            return respuesta_error(
                "USR404",
                "Not Found",
                "No existe un usuario con ese id."
            ), 404

        return jsonify(usuario), 200

    except mysql.connector.Error as error:
        return respuesta_error(
            "USR500",
            "Internal Server Error",
            f"Error al obtener el usuario: {error}"
        ), 500

    finally:
        cursor.close()
        conexion.close()


@usuarios_blueprint.route("/usuarios/<int:id>", methods=["PUT"])
def reemplazar_usuario(id):
    data = request.get_json(silent=True)

    if not data:
        return respuesta_error(
            "USR400",
            "Bad Request",
            "El body debe ser JSON válido."
        ), 400

    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return respuesta_error(
            "USR401",
            "Bad Request",
            "Los campos 'nombre' y 'email' son obligatorios."
        ), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.execute(
                "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s",
                (nombre, email, id)
            )
        else:
            cursor.execute(
                "INSERT INTO usuarios (id, nombre, email) VALUES (%s, %s, %s)",
                (id, nombre, email)
            )

        conexion.commit()
        return "", 204

    except mysql.connector.Error as error:
        if error.errno == 1062:
            return respuesta_error(
                "USR409",
                "Conflict",
                "Ya existe un usuario con ese email."
            ), 409

        return respuesta_error(
            "USR500",
            "Internal Server Error",
            f"Error al reemplazar el usuario: {error}"
        ), 500

    finally:
        cursor.close()
        conexion.close()


@usuarios_blueprint.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()

        if not usuario:
            return respuesta_error(
                "USR404",
                "Not Found",
                "No existe un usuario con ese id."
            ), 404

        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conexion.commit()

        return "", 204

    except mysql.connector.Error as error:
        return respuesta_error(
            "USR500",
            "Internal Server Error",
            f"Error al eliminar el usuario: {error}"
        ), 500

    finally:
        cursor.close()
        conexion.close()
