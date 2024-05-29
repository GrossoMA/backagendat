from flask import Blueprint, request, send_file
from ..models.imagen import Imagen

imagen_blueprint = Blueprint('imagen', __name__)

@imagen_blueprint.route('/cargar', methods=['POST'])
def cargar_imagen():
    if 'imagen' not in request.files:
        return 'No hay archivo de imagen', 400
    archivo = request.files['imagen']
    # Aquí podrías crear una instancia de tu clase Imagen y guardarla
    imagen = Imagen(archivo)
    imagen.guardar_como_jpg()
    imagen.optimizar()
    return 'Imagen cargada con éxito', 200

@imagen_blueprint.route('/<nombre>', methods=['GET'])
def obtener_imagen(nombre):
    # Aquí implementarías la lógica para recuperar y enviar la imagen solicitada
    path_imagen = 'ruta/a/tu/imagen/' + nombre
    return send_file(path_imagen, mimetype='image/jpeg')