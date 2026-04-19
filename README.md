# Instrucciones para levantar y probar el backend

## 1. Requisitos

Tener instalado:

* Python 3
* pip
* DataGrip
* MySQL Server
* git

## 2. Clonar el repositorio

bash id="vvjdl7"
git clone https://github.com/Guillermo-Gutierrezfiuba/TP-BACKENDfiuba.git
cd TP-BACKENDfiuba


## 3. Crear y activar entorno virtual

Si no existe .venv:

bash id="sjr6wb"
python3 -m venv .venv


Activarlo:

bash id="j3jiu8"
source .venv/bin/activate


## 4. Instalar dependencias

bash id="2j5e2a"
pip install -r requirements.txt


Si por alguna razón falla, instalar manualmente:

bash id="ibfmhn"
python -m pip install flask mysql-connector-python python-dotenv


## 5. Crear base de datos en MySQL

Iniciar MySQL:

bash id="cnw5n3"
sudo service mysql start
sudo mysql

## 5.1 Ejecutar el programa que crea las tablas de mysql

python3 tablas.sql

## 5.2 Conectar esto en DataGrip para poder despues visualizar las tablas creadas

Abrir DataGrip:
crear conexion data source con mysql
ingresar los datos de conexion con mysql server
añadir consola  en new, query console
copiar el codigo de tablas.sql y ejecutar
podra visualizar las tablas


## 6. Crear el archivo .env

En la raíz del proyecto, crear un archivo llamado .env con este contenido:

env id="20gt87"
DB_HOST=localhost
DB_USER=prode_user
DB_PASSWORD=tu_password
DB_NAME=prode_api


## 7. Levantar la aplicación

Desde la carpeta del proyecto:

bash id="d1qbia"
python app.py


Si todo está bien, la app va a correr en:

bash id="evflp3"
http://127.0.0.1:5000


## 8. Pruebas con bruno

### 8.1 Crear usuario



### 8.2 Listar usuarios



### 8.3 Obtener usuario por id




### 8.4 Crear partido




### 8.5 Listar partidos




### 8.6 Obtener partido por id




### 8.7 Crear predicción

Esto hay que hacerlo antes de cargar el resultado del partido.



### 8.8 Cargar resultado del partido




La respuesta esperada es:


HTTP/1.1 204 NO CONTENT


### 8.9 Consultar ranking




La respuesta debería ser algo parecido a esto:

json id="k86mey"
{
  "ranking": [
    {
      "id_usuario": 1,
      "puntos": 3
    }
  ],
  "_links": {
    "_first": {
      "href": "/ranking?_limit=10&_offset=0"
    },
    "_last": {
      "href": "/ranking?_limit=10&_offset=0"
    },
    "_next": null,
    "_prev": null
  }
}


## 9. Orden correcto para probar

El orden recomendado es:

1. Crear usuario
2. Crear partido
3. Crear predicción
4. Cargar resultado
5. Consultar ranking

Si se carga el resultado antes de la predicción, después ya no va a dejar predecir ese partido.
