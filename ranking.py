from urllib.parse import urlencode

from flask import Blueprint, jsonify, request

from db import obtener_conexion

ranking_blueprint = Blueprint("ranking", __name__)


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


def construir_links(base_path, limit, offset, total):
    last_offset = ((total - 1) // limit) * limit if total > 0 else 0

    def build(off):
        return {"href": f"{base_path}?{urlencode({'_limit': limit, '_offset': off})}"}

    return {
        "_first": build(0),
        "_last": build(last_offset),
        "_next": build(offset + limit) if offset + limit < total else None,
        "_prev": build(offset - limit) if offset - limit >= 0 else None,
    }


@ranking_blueprint.route("/ranking", methods=["GET"])
def obtener_ranking():
    limit, offset, error = leer_paginacion()
    if error:
        return error

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM (
                SELECT pr.usuario_id
                FROM predicciones pr
                JOIN partidos p ON pr.partido_id = p.id
                WHERE p.goles_local IS NOT NULL AND p.goles_visitante IS NOT NULL
                GROUP BY pr.usuario_id
            ) AS subconsulta
            """
        )
        total = cursor.fetchone()["total"]

        if total == 0:
            return "", 204

        cursor.execute(
            """
            SELECT
                pr.usuario_id AS id_usuario,
                CAST(SUM(
                    CASE
                        WHEN pr.goles_local = p.goles_local
                             AND pr.goles_visitante = p.goles_visitante THEN 3
                        WHEN (
                            (pr.goles_local > pr.goles_visitante AND p.goles_local > p.goles_visitante)
                            OR
                            (pr.goles_local < pr.goles_visitante AND p.goles_local < p.goles_visitante)
                            OR
                            (pr.goles_local = pr.goles_visitante AND p.goles_local = p.goles_visitante)
                        ) THEN 1
                        ELSE 0
                    END
                ) AS SIGNED) AS puntos
            FROM predicciones pr
            JOIN partidos p ON pr.partido_id = p.id
            WHERE p.goles_local IS NOT NULL AND p.goles_visitante IS NOT NULL
            GROUP BY pr.usuario_id
            ORDER BY puntos DESC, pr.usuario_id ASC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        ranking = cursor.fetchall()

        for fila in ranking:
            fila["puntos"] = int(fila["puntos"])

        return jsonify({
            "ranking": ranking,
            "_links": construir_links("/ranking", limit, offset, total)
        }), 200

    except Exception as e:
        return respuesta_error(str(e), 500)

    finally:
        cursor.close()
        conexion.close()
