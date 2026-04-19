from urllib.parse import urlencode
from datetime import datetime, date

from flask import Blueprint, jsonify, request

from db import obtener_conexion

partidos_blueprint = Blueprint("partidos", __name__)


def respuesta_error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


def leer_paginacion():
    try:
        limit = int(request.args.get("_limit", request.args.get("limit", 10)))
        offset = int(request.args.get("_offset", request.args.get("offset", 0)))
    except ValueError:
        return None, None, respuesta_error("Paginacion invalida", 400)

    if limit <= 0 or offset < 0:
        return None, None, respuesta_error("Paginacion invalida", 400)

    return limit, offset, None


def construir_links(base_path, limit, offset, total, filtros=None):
    if filtros is None:
        filtros = {}

    last_offset = ((total - 1) // limit) * limit if total > 0 else 0

    def build(off):
        params = {"_limit": limit, "_offset": off}
        for clave, valor in filtros.items():
            if valor is not None:
                params[clave] = valor
        return {"href": f"{base_path}?{urlencode(params)}"}

    return {
        "_first": build(0),
        "_last": build(last_offset),
        "_next": build(offset + limit) if offset + limit < total else None,
        "_prev": build(offset - limit) if offset - limit >= 0 else None,
    }


def serializar_fecha(valor):
    if isinstance(valor, datetime):
        return valor.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(valor, date):
        return valor.strftime("%Y-%m-%d")
    return valor


def serializar_partido(partido):
    if not partido:
        return partido

    copia = dict(partido)
    if "fecha" in copia:
        copia["fecha"] = serializar_fecha(copia["fecha"])
    return copia


def obtener_campos_resultado(data):
    local = data.get("local", data.get("goles_local"))
    visitante = data.get("visitante", data.get("goles_visitante"))
    return local, visitante


def obtener_campos_prediccion(data):
    id_usuario = data.get("id_usuario", data.get("usuario_id"))
    local = data.get("local", data.get("goles_local"))
    visitante = data.get("visitante", data.get("goles_visitante"))
    return id_usuario, local, visitante


@partidos_blueprint.route("/partidos", methods=["POST"])
def crear_partido():
    data = request.get_json(silent=True)

    if not data:
        return respuesta_error("Body JSON requerido", 400)

    if not all(campo in data for campo in ("equipo_local", "equipo_visitante", "fecha", "fase")):
        return respuesta_error("Faltan datos", 400)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["equipo_local"],
                data["equipo_visitante"],
                data["fecha"],
                data["fase"],
            ),
        )
        conexion.commit()
        partido_id = cursor.lastrowid

        return jsonify({
            "id": partido_id,
            "equipo_local": data["equipo_local"],
            "equipo_visitante": data["equipo_visitante"],
            "fecha": data["fecha"],
            "fase": data["fase"],
        }), 201

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()


@partidos_blueprint.route("/partidos", methods=["GET"])
def listar_partidos():
    limit, offset, error = leer_paginacion()
    if error:
        return error

    equipo = request.args.get("equipo")
    fecha = request.args.get("fecha")
    fase = request.args.get("fase")

    where = []
    params = []

    if equipo:
        where.append("(equipo_local LIKE %s OR equipo_visitante LIKE %s)")
        params.extend([f"%{equipo}%", f"%{equipo}%"])

    if fecha:
        where.append("DATE(fecha) = %s")
        params.append(fecha)

    if fase:
        where.append("fase = %s")
        params.append(fase)

    where_sql = ""
    if where:
        where_sql = " WHERE " + " AND ".join(where)

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT COUNT(*) AS total FROM partidos" + where_sql,
            params,
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            """
            SELECT id, equipo_local, equipo_visitante, fecha, fase
            FROM partidos
            """
            + where_sql
            + """
            ORDER BY fecha ASC, id ASC
            LIMIT %s OFFSET %s
            """,
            params + [limit, offset],
        )
        partidos = cursor.fetchall()

        partidos_serializados = [serializar_partido(partido) for partido in partidos]

        links = construir_links(
            "/partidos",
            limit,
            offset,
            total,
            {"equipo": equipo, "fecha": fecha, "fase": fase},
        )

        return jsonify({
            "partidos": partidos_serializados,
            "_links": links
        }), 200

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()


@partidos_blueprint.route("/partidos/<int:id>", methods=["GET"])
def obtener_partido(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, equipo_local, equipo_visitante, fecha, fase, goles_local, goles_visitante
            FROM partidos
            WHERE id = %s
            """,
            (id,),
        )
        partido = cursor.fetchone()

        if not partido:
            return respuesta_error("No encontrado", 404)

        return jsonify(serializar_partido(partido)), 200

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()


@partidos_blueprint.route("/partidos/<int:id>", methods=["DELETE"])
def eliminar_partido(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))
        conexion.commit()

        if cursor.rowcount == 0:
            return respuesta_error("No encontrado", 404)

        return "", 204

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()


@partidos_blueprint.route("/partidos/<int:id>/resultado", methods=["PUT"])
def actualizar_resultado(id):
    data = request.get_json(silent=True)

    if not data:
        return respuesta_error("Body JSON requerido", 400)

    local, visitante = obtener_campos_resultado(data)

    if local is None or visitante is None:
        return respuesta_error("Faltan datos", 400)

    try:
        local = int(local)
        visitante = int(visitante)
    except (TypeError, ValueError):
        return respuesta_error("Los goles deben ser enteros", 400)

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        partido = cursor.fetchone()

        if not partido:
            return respuesta_error("Partido no existe", 404)

        cursor.execute(
            """
            UPDATE partidos
            SET goles_local = %s, goles_visitante = %s
            WHERE id = %s
            """,
            (local, visitante, id)
        )
        conexion.commit()

        return "", 204

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()


@partidos_blueprint.route("/partidos/<int:id>/prediccion", methods=["POST"])
def crear_prediccion(id):
    data = request.get_json(silent=True)

    if not data:
        return respuesta_error("Body JSON requerido", 400)

    id_usuario, local, visitante = obtener_campos_prediccion(data)

    if id_usuario is None or local is None or visitante is None:
        return respuesta_error("Faltan datos", 400)

    try:
        id_usuario = int(id_usuario)
        local = int(local)
        visitante = int(visitante)
    except (TypeError, ValueError):
        return respuesta_error("Los valores de la prediccion deben ser enteros", 400)

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, goles_local, goles_visitante
            FROM partidos
            WHERE id = %s
            """,
            (id,),
        )
        partido = cursor.fetchone()

        if not partido:
            return respuesta_error("Partido no existe", 404)

        if partido["goles_local"] is not None or partido["goles_visitante"] is not None:
            return respuesta_error("El partido ya fue jugado", 409)

        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            return respuesta_error("Usuario no existe", 404)

        cursor.execute(
            """
            SELECT id
            FROM predicciones
            WHERE partido_id = %s AND usuario_id = %s
            """,
            (id, id_usuario),
        )
        prediccion_existente = cursor.fetchone()

        if prediccion_existente:
            return respuesta_error("Ya existe una prediccion para este usuario y partido", 409)

        cursor.execute(
            """
            INSERT INTO predicciones (partido_id, usuario_id, goles_local, goles_visitante)
            VALUES (%s, %s, %s, %s)
            """,
            (id, id_usuario, local, visitante),
        )
        conexion.commit()

        prediccion_id = cursor.lastrowid

        return jsonify({
            "id": prediccion_id,
            "partido_id": id,
            "id_usuario": id_usuario,
            "local": local,
            "visitante": visitante
        }), 201

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()
