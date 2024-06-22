from functools import wraps
from flask import request, jsonify
import jwt
from api import app
from api.db.db import mysql


    

def token_required(func):
    #funcion que se invoca cada vez que se requiera un token
    @wraps(func)
    def decorated(*args, **kwargs):
        print(kwargs)
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({"message": "Falta el token"}), 401
        
        user_id = None

        if 'user-id' in request.headers:
            user_id = request.headers['user-id']

        if not user_id:
            return jsonify({"message": "Falta el usuario"}), 401
        
        try:
            data = jwt.decode(token , app.config['SECRET_KEY'], algorithms = ['HS256'])
            token_id = data['id']

            if int(user_id) != int(token_id):
                print("ok")
                return jsonify({"message": "Error de id"}), 401
            
        except Exception as e:
            print("reeror",e)
            return jsonify({"message": str(e)}), 401

        return func(*args, **kwargs)
    return decorated

def client_resource(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print("Argumentos en client_resource: ", kwargs)
        id_cliente = kwargs['client_id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario FROM clientes WHERE id_cliente = {0}'.format(id_cliente)) 
        data = cur.fetchone()
        cur.close()
        if data:
            """ print(data) """
            id_prop = data[0]
            user_id = request.headers['user-id']
            print("id prop ",id_prop,"user id ",user_id)
            if int(id_prop) != int(user_id):
                return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated
def evento_resource(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print("Argumentos en evento_resource: ", kwargs)
        id_evento = kwargs['evento_id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario FROM eventos WHERE id_evento = {0}'.format(id_evento)) 
        data = cur.fetchone()
        cur.close()
        if data:
            """ print(data) """
            id_prop = data[0]
            user_id = request.headers['user-id']
            print("id prop ",id_prop,"user id ",user_id)
            if int(id_prop) != int(user_id):
                return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated

def user_resources(func):
    """
    Decorador para recursos de usuario que verifica si el usuario está autorizado.

    Args:
        func (invocada): la función a invocar.

    Returns:
        invocada: función invocada con la lógica de autorización.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        print("Argumentos en user_resources: ", kwargs)
        id_user_route = int(kwargs['user_id'])  # Obtiene el ID de usuario del recurso solicitado (proveniente del front-end)
        # Obtiene el ID de usuario autenticado a través de las cabeceras de la solicitud        
        user_id = request.headers['user-id'] 
        
        if int(id_user_route) != int(user_id): # Compara los ID de usuario para verificar la autorización
            return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        
        return func(*args, **kwargs) # Ejecuta la función original si la autorización es exitosa
    return decorated

def oferta_resource(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print("Argumentos en oferta_resource: ", kwargs)
        id_oferta = kwargs['oferta_id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario FROM oferta WHERE id_oferta = {0}'.format(id_oferta)) 
        data = cur.fetchone()
        cur.close()
        if data:
            """ print(data) """
            id_prop = data[0]
            user_id = request.headers['user-id']            
            if int(id_prop) != int(user_id):
                return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated

def factura_resource(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print("Argumentos en oferta_resource: ", kwargs)
        id_factura = kwargs['factura_id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_usuario FROM facturas WHERE id_factura = {0}'.format(id_factura)) 
        data = cur.fetchone()
        cur.close()
        if data:
            """ print(data) """
            id_prop = data[0]
            user_id = request.headers['user-id']            
            if int(id_prop) != int(user_id):
                return jsonify({"message": "No tiene permisos para acceder a este recurso"}), 401
        return func(*args, **kwargs)
    return decorated

def authorize_municipio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('user-id')
        user = get_user_from_db(user_id)  # Obtener usuario de la base de datos
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        municipio_id = kwargs.get('municipio_id')
        if user['id_municipio'] != municipio_id and user['role'] != 'admin':
            return jsonify({'message': 'Unauthorized access'}), 403
        
        return f(*args, **kwargs)
    return decorated_function