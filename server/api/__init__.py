from flask import Flask
from flask_cors import CORS


#creamos app
app = Flask(__name__)
# Modelo cors. para controlar permisos para acceder a tus recursos
# Habilita CORS para todos los dominios
CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

app.config['SECRET_KEY'] = 'app_123'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

import api.routes.client
import api.routes.users
import api.routes.oferta
import api.routes.factura
import api.routes.eventos
import api.routes.localidades
import api.routes.municipios
