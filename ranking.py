from flask import Blueprint, jsonify
from database.db import obtener_conexion

ranking_blueprint = Blueprint('ranking', __name__)

@ranking_blueprint.route('/ranking', methods=['GET'])
def obtener_ranking():
    conexion= obtener_conexion
    cursor = conexion.cursor(dictionary=True)


    cursor.execute(""" SELECT  u.id, u.nombre, COUNT(p.id) AS total_predicciones, SUM(CASE WHEN pr.goles_local = pa.goles_local AND pr.goles_visitante = pa.goles_visitante  THEN 3 WHEN (pr.goles_local - pr_goles_visitante) = (pa.goles_local - pa.goles_visitante) THEN 1  ELSE 0  END) AS puntos  FROM usuarios u  LEFT JOIN predicciones pr ON   u.id = pr.usuario_id  LEFT JOIN partidos pa ON  pr.partido_id = pa.id  GROUP BY u.id, u.nombre  ORDER BY puntos DESC"""))

    ranking = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(ranking)
    