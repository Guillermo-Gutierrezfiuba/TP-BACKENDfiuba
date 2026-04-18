from flask import Blueprint, jsonify
from database.db import get_connection

partidos_blueprint = Blueprint('partidos', __name__)



@partidos_blueprint.route('/partidos', methods=['POST'])
def crear_partido():
    data = request.json  #agarramos el cuerpo de la request, lo que se manda de bruno

    if not all(datos in data for datos in("equipo_local", "equipo_visitante", "fecha","fase")):
        return jsonify({"error": "Faltan datos"}), 400


    """validamos que en el cuerpo de la request se haya añadido todos los valores, 
    en caso de que no se hayan enviado desde bruno todos los valores, se devuelve un 400, bad request 
    """

    # se conecta  a la base de datos y se empieza a utilizar cursor, herramienta para programar cosas de sql
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(""" INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase)
    VALUES(%s, %s, %s, %s)""", (data['equipo_local'], data['equipo_visitante'], data['fecha'], data['fase']))
    
    """ aca lo que sucede es lo siguiente: se ejecuta el metodo insert de sql/datagrip pero los valores son placeholders:%s
    es como una especie de valor seguro que se especifica en sql al ejecutar esto, se insertara en la tabla partidos
    1 fila con los datos de las claves de los diccionarios de esa tupla
    """

    conexion.commit() # se guardan los cambios
    cursor.close()
    conexion.close() # se termina la conexion y el cursor, una buena practica

    return jsonify({"mensaje": "Partido creado"}), 201 #creado correctamente



@partidos_blueprint.route('/partidos', methods=['GET'])
def listar_partidos():
    conexion = obtener_conexion
    cursor = conexion.cursor(dictionary=True)

    equipo = request.args.get('equipo')
    fecha = request.args.get('fecha')
    fase = request.args.get('fase')

    query = "SELECT * FROM partidos WHERE 1=1"

    parametros = []

    if equipo:
        query += "AND (equipo_local = %s OR equipo_visitante = %s)"
        parametros.extend([equipo,equipo])
        
    
    if fecha:
        query += " AND fecha=%s"
        parametros.append(fecha)
    
    if fase:
        query += " AND fase=%s"
        parametros.append(fase)
    
    
    cursor.execute(query, parametros)
    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify(resultados)


@partidos_blueprint.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)


    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not partido:
        return jsonify({"error": "No encontrado"}), 404
    
    return jsonify(partido)


@partidos_blueprint.route('/partidos/<int:id>', methods=['DELETE'])
def eliminar_partido(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({"mensaje":"Partido eliminado"})



@partidos_blueprint.route('/partidos/<int:id>/resultado', methods=['PUT'])
def cargar_resultado(id):
    data = request.json

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(""" UPDATE partidos SET goles_local = %s, goles_visitante = %s WHERE id = %s""", (data['goles_local'], data['goles_visitante'], id))


    conexion.commit()
    conexion.close()
    cursor.close()

    return jsonify({"mensaje": "Resultado Actualizado"})


@partidos_blueprint.route('/partidos/<int:id>/prediccion', methods=['POST'])
def crear_prediccion(id):
    data = request.json

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id))
    partido = cursor.fetchone()


    if not partido:
        cursor.close()
        conexion.close()
        return jsonify({"error": "Partido no existe"}), 404
    
    if partido['goles_local'] is not None:
        cursor.close()
        conexion.close()
        return jsonify({"error": "El partido ya se jugó"}), 400
    
    try:
        cursor.execute(""" INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante) VALUES (%s, %s, %s, %s)""", (data['usuario_id'], data['goles_local'], data['goles_visitante']))
        conexion.commit()
    except:
        cursor.close()
        conexion.close()
        return jsonify({"error": "Predicción duplicada"}), 400

    conexion.close()    
    cursor.close()
    
    return jsonify({"mensaje": "Prediccion creada"}), 201

    

