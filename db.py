import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

"""
Este codigo sirve para conectar Flask con MySQL.
Los datos de conexion se leen desde el archivo .env
para que cada integrante del grupo pueda usar su propia configuracion local.
"""

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        if conexion.is_connected():
            print("Conexion exitosa")
            return conexion
        else:
            print("Error al conectar a la base de datos")
            return None

    except mysql.connector.Error as error:
        print(f"Error al conectar a la base de datos: {error}")
        return None


def desconectar(conexion):
    if conexion is not None and conexion.is_connected():
        conexion.close()
        print("Conexion cerrada")
