# from flask import Flask
# from flask_cors import CORS


# #creamos app
# app = Flask(__name__)
# # Modelo cors. para controlar permisos para acceder a tus recursos
# # Habilita CORS para todos los dominios
# CORS(app)
# # CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
from flask import Flask
from flask_cors import CORS


# para crear app
def create_app():
    print("----------------------------------------------------------------")
    app = Flask(__name__)
    # Modelo cors. para controlar permisos para acceder a tus recursos
    # Habilita CORS para todos los dominios
    CORS(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    #CORS(app, resources={r"/*": {"origins": "https://grossoma.github.io/frontagendat/"}})
    return app

app = create_app()
app.config['SECRET_KEY'] = 'app_123'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


import api.routes.users
import api.routes.eventos
import api.routes.localidades
import api.routes.municipios
