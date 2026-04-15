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
    return mysql.connector.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
    