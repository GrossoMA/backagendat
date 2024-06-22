from api import app
from api.models.user import User
from flask import request, jsonify
from api.utils import token_required, client_resource, user_resources
from api.db.db import mysql
import jwt
import datetime

@app.route('/login', methods = ['POST'])
def login():
    print("print [0]")
    auth = request.authorization
    print(auth)

    """ Control: existen valores para la autenticacion? """
    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "No autorizado"}), 401

    """ Control: existe y coincide el usuario en la BD? """
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE nombreusuario = %s AND contrasenia = %s', (auth.username, auth.password))
    row = cur.fetchone()

    if not row:
       return jsonify({"message": "Error en el nombre de usuario y/o contraseña"}), 401

    """ El usuario existe en la BD y coincide su contraseña """
    print("print row[0]",row[0])
    token = jwt.encode({'id': row[0],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=100)}, app.config['SECRET_KEY'])
    print("token",token)
    print("row",row[0])
    print('entro')
    return jsonify({"token": token, "username": auth.username , "id": row[0]})

# Ruta de prueb
# @app.route('/users')
# def get_all():
#     cursor = mysql.connection.cursor()
#     cursor.execute('SELECT * FROM usuarios')
#     data = cursor.fetchall()
#     cursor.close()

#     return str(data)


# @app.route('/users', methods = ['POST'])
# def create_user():
#     try:
#         cur = mysql.connection.cursor()
#         cur = mysql.connection.cursor()
#         data = request.get_json()
#         message = "message"

#         # Se verifica si el usuario ya existe
#         cur.execute("SELECT * FROM usuarios WHERE nombreusuario = %s", (data['nombreusuario'],))
#         usuario_existente = cur.fetchone()

#         if usuario_existente:
#             return {message: "El usuario ya existe."}, 400

#         CAMPOS_REQUERIDOS = ['nombreusuario', 'contrasenia', 'nombre', 'apellido', 'dni', 'telefono', 'email']
#         # Se comprueban que los campos estén completos
#         if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS):
#             return jsonify({message: "Datos incompletos"}), 400

#         # Insertar nuevo usuario
#         cur.execute("INSERT INTO usuarios (nombreusuario, contrasenia, nombre, apellido, dni, telefono, email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                     (data['nombreusuario'], data['contrasenia'], data['nombre'], data['apellido'], data['dni'],
#                      data['telefono'], data['email']))

#         mysql.connection.commit()
#         cur.close()
#         return {message: "Usuario creado exitosamente"}, 201

#     except Exception as e:
#         return str(e), 500 #Error interno del servidor


# @app.route('/users/<int:user_id>', methods=['PUT'])
# @token_required
# @user_resources
# def update_user(user_id):
#     try:
#         cur = mysql.connection.cursor()
#         # Se verifica si el usuario existe antes de actualizar
#         cur.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,)) #Verifica si existe usuario
#         usuario_existente = cur.fetchone()
#         if not usuario_existente:
#             return {"message": "Usuario no encontrado."}, 404

#         data = request.get_json()
#         # Se actualizan los datos del usuario en la BDD
#         cur.execute("UPDATE usuarios SET nombreusuario = %s, contrasenia = %s, nombre = %s, apellido = %s, dni = %s, telefono = %s, email = %s WHERE id_usuario = %s",
#                     (data['nombreusuario'], data['contrasenia'], data['nombre'], data['apellido'], data['dni'],
#                      data['domicilio'], data['telefono'], data['email']))
#         mysql.connection.commit()
#         cur.close()

#         return {"message": "Usuario actualizado exitosamente"}, 200
#     except Exception as e:
#         return str(e), 500  # Error interno del servidor


# @app.route('/users/<int:user_id>', methods=['DELETE'])
# @token_required
# @user_resources
# def delete_user(user_id):
#     try:
#         cur = mysql.connection.cursor()
#         # Verificar si el usuario existe antes de eliminar
#         cur.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
#         usuario_existente = cur.fetchone()

#         if not usuario_existente:
#             return {"message": "Usuario no encontrado."}, 404
#         cur.execute("UPDATE usuarios SET estado = %s WHERE id_usuario = %s", (0,user_id,)) # Eliminar el usuario
#         mysql.connection.commit()
#         cur.close()
#         return {"message": "Usuario eliminado exitosamente"}, 200
#     except Exception as e:
#         return str(e), 500  # Error interno del servidor


