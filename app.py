 from flask import Flask  #importo flask

#agarramos cada 'paquete' de endpoints: /partidos, /usuarios y el ranking

 from routes.partidos import partidos_blueprint
 from routes.usuarios import usuarios_blueprint
 from routes.ranking import ranking_blueprint

 app = Flask(__name__)

#conectamos esos modulos a la app para que pueda usarse

 app.register_blueprint(partidos_blueprint)
 app.register_blueprint(usuarios_blueprint)
 app.register_blueprint(ranking_blueprint)

#ejecutamos el program
 if __name__ == "__main__":
    app.run(debug==True)
 