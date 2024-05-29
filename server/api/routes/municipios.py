from api import app
from api.models.municipio import Municipio
from flask import jsonify, request #permite devolver json
from api.utils import token_required, user_resources
from api.db.db import mysql
import MySQLdb

# aca podria controlar datos para verificar que el usuario es admin, y que esta activo
def es_admin(user):
    return False
    

@app.route('/user/<int:user_id>/municipios', methods=['GET'])
@token_required
@user_resources
def get_municipio_by_user_id(user_id):
    es_usuario_admin = es_admin(user_id)  # TODO  esta función verifica si el usuario es admin

    if es_usuario_admin:
        consulta_base = 'SELECT * FROM municipios m'  # Los admin obtienen todos los municipios
        parametros = []
    else:
        # Si el usuario no es admin, ajustamos la consulta para recuperar el municipio asociado
        consulta_base = '''SELECT m.* 
                           FROM municipios m 
                           '''
        # INNER JOIN usuarios u ON m.id_municipio = u.id_municipio                           WHERE u.id_usuario = %s
        parametros = []#parametros = [user_id]

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(consulta_base, parametros)
    data = cur.fetchall()
    print("----------------------------------------------------------------")
    print("respondiendo a get municipio")
    print("----------------------------------------------------------------")

    municipiostList = [Municipio(row).to_json() for row in data]

    if municipiostList:
        return jsonify(municipiostList)
    else:
        return jsonify({"message": "No se encontraron municipios para el usuario"}), 404
    

@app.route('/user/<int:user_id>/municipios', methods=['POST'])
@token_required
@user_resources
def create_municipio(user_id):
    es_usuario_admin = es_admin(user_id)  # Esta función verifica si el usuario es admin

    # Solo permitir a los administradores crear municipios
    if not es_usuario_admin:
        return jsonify({"message": "No tienes permisos para crear municipios"}), 403

    try:
        CAMPOS_REQUERIDOS = ['nombre_municipio']

        # Captura los datos en formato JSON
        data = request.get_json()

        # Encuentra los campos que faltan
        campos_faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in data]
        if campos_faltantes:
            # Devuelve un mensaje con los campos faltantes
            return jsonify({"message": "Faltan campos en la solicitud", "campos_faltantes": campos_faltantes}), 400

        # Verificar duplicados
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM municipios WHERE nombre_municipio = %s', (data['nombre_municipio'].upper(),))
        if cur.fetchone():
            cur.close()
            return jsonify({"message": "El municipio ya existe"}), 409

        # Inserta el municipio en la base de datos
        consulta = 'INSERT INTO municipios (nombre_municipio) VALUES (%s)'
        valores = (data['nombre_municipio'].upper(),)
        cur.execute(consulta, valores)
        id_municipio = cur.lastrowid
        mysql.connection.commit()

        # Retorna el mensaje con el ID del municipio creado
        return jsonify({"message": "Municipio creado exitosamente", "id_municipio": id_municipio}), 201

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        print("error:", str(e))
        return jsonify({"message": "Municipio no agregado"}), 500
    finally:
        if cur is not None:
            cur.close()

# para taer los municipios que se ajusten a la busqueda x el nombre
# /user/1/municipios/buscar?nombre=ia 
@app.route('/user/<int:user_id>/municipios/buscar', methods=['GET'])
@token_required
@user_resources
def buscar_municipio_por_nombre(user_id):
    nombre_municipio = request.args.get('nombre', '')  # Obtener el nombre del municipio de los parámetros de consulta
    es_usuario_admin = es_admin(user_id)  # verificar si el usuario es admin

    # consulta base y los parámetros según si el usuario es admin o no
    if es_usuario_admin:
        consulta_base = "SELECT * FROM municipios WHERE nombre_municipio LIKE %s"  # Los admin pueden buscar cualquier municipio
    else:
        # consulta_base = "SELECT * FROM municipios WHERE id_usuario = %s AND nombre_municipio LIKE %s"  # Usuarios regulares buscan en sus municipios
        consulta_base = '''SELECT m.* 
                           FROM municipios m 
                           INNER JOIN usuarios u ON m.id_municipio = u.id_municipio
                           WHERE u.id_usuario = %s 
                           AND nombre_municipio LIKE %s'''
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Ajustar los parámetros de la consulta según si el usuario es admin
    parametros = [f"%{nombre_municipio}%"] if es_usuario_admin else [user_id, f"%{nombre_municipio}%"]
    cur.execute(consulta_base, parametros)
    data = cur.fetchall()

    municipiostList = [Municipio(row).to_json() for row in data]

    if municipiostList:
        return jsonify(municipiostList)
    else:
        return jsonify({"message": "No se encontró el municipio buscado"}), 404
    


