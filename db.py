from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

"""
todo este codigo sirve para poder conectar mysql y flask
y laburar, el problema es que mysql pide un usuario = 'root'
y una contraseña que es distinta para cada 1, este codigo hace que con un programa
'.env' que tiene info global nos permita usar a cada uno la contra que queramos

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
    return mysql.connector.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))

def desconectar(conexion):
    if conexion.is_connected():
        conexion.close()
        print("Conexion cerrada")