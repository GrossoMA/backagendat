from api import app
from api.models.localidad import Localidad
from flask import jsonify, request #permite devolver json
from api.utils import token_required, user_resources
from api.db.db import mysql
import MySQLdb

# aca podria controlar datos para verificar que el usuario es admin, y que esta activo
def es_admin(user):
    return True
    

# @app.route('/user/<int:user_id>/municipios/<int:municipio_id>/localidades/', methods=['GET'])
@app.route('/user/<int:user_id>/localidades', methods=['GET'])
@token_required
@user_resources
#@municipio_resources TODO: implementar esto luego
def get_all_localidades_by_user_id(user_id):
    es_usuario_admin = es_admin(user_id)  # Asume que esta función verifica si el usuario es admin
    municipio_id = 1

    if es_usuario_admin:
        consulta_base = 'SELECT * FROM localidades l'  # Los admin obtienen todas los localidades        
        parametros = []
        print(municipio_id,"estoy x aca en localidades query") #)
    elif municipio_id > 1:
        print(municipio_id,"estoy x aca") #)
        # consulta_base = 'SELECT * FROM localidades WHERE id_municipio = %s AND id_usuario = %s'  # Usuarios regulares ven solo sus localidades
        consulta_base = '''SELECT l.*
                           FROM localidades l
                           INNER JOIN municipios m ON m.id_municipio = l.id_municipio
                           INNER JOIN usuarios u ON u.id_municipio =  m.id_municipio                           
                           WHERE u.id_usuario = %s 
                           AND id_municipio = %s'''
        parametros = [user_id,municipio_id]
    else:
        return jsonify({"message": "No tienes permisos para acceder a este recurso"}), 403
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(consulta_base, parametros)
    print("----------------------------------------------------------------")
    print("respondiendo a get localidades")
    print("----------------------------------------------------------------")
    data = cur.fetchall()

    localidadestList = [Localidad(row).to_json() for row in data]

    if localidadestList:
        print("----------------------------------------------------------------")
        print(localidadestList)
        return jsonify(localidadestList)
    else:
        return jsonify({"message": "No se encontraron localidades"}), 404
    

#CREAR UN NUEVA LOCALIDAD
@app.route('/user/<int:user_id>/municipios/<int:municipio_id>/localidades', methods=['POST'])
@token_required
@user_resources
#@municipio_resources TODO: implementar esto luego
def create_localidad(user_id,municipio_id):
    es_usuario_admin = es_admin(user_id)  # Esta función verifica si el usuario es admin

    # Solo permitir a los administradores crear municipios
    if not es_usuario_admin:
        return jsonify({"message": "No tienes permisos para crear localidades"}), 403    

    try:
        CAMPOS_REQUERIDOS = ['nombre_localidad']
        
        # Captura los datos en formato JSON
        data = request.get_json()
        print(data)

        # Encuentra los campos que faltan
        campos_faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in data]

        if campos_faltantes:
            # Devuelve un mensaje con los campos faltantes
            return jsonify({"message": "Faltan campos en la solicitud", "campos_faltantes": campos_faltantes}), 400

        # Se comprueban que los campos estén completos
        if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS):           
                return jsonify({"message"}), 400
        
        # Aca TODO ver la posibilidad de controlar localidades duplicadas
        
        # Crea una instancia de Localidad  
        new_localidad = {
            'nombre_localidad': data['nombre_localidad'].upper(),
        }

        
        # Conecta con la base de datos
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Inserta el localidad en la base de datos
        consulta = 'INSERT INTO localidades (nombre_localidad,id_municipio) VALUES (%s,%s)'
        valores = (new_localidad['nombre_localidad'],municipio_id)
        
        cur.execute(consulta, valores)

        # Obtiene el último ID insertado
        id_localidad = cur.lastrowid

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()              

        # Retorna el mensaje con el ID del localidad creado
        return jsonify({"message": "Localidad creada exitosamente"}), 201

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        print("error:", str(e))
        return jsonify({"message": "Localidad no agregada"}), 500

# para taer los localidades que se ajusten a la busqueda x el nombre
# /user/1/localidades/buscar?nombre=ia 
@app.route('/user/<int:user_id>/localidades/buscar', methods=['GET'])
@token_required
@user_resources
def buscar_localidad_por_nombre(user_id):
    nombre_localidad = request.args.get('nombre', '')  # Obtener el nombre del localidad de los parámetros de consulta
    es_usuario_admin = es_admin(user_id)  # verificar si el usuario es admin

    # consulta base y los parámetros según si el usuario es admin o no
    if es_usuario_admin:
        consulta_base = "SELECT * FROM localidades WHERE nombre_localidad LIKE %s"  # Los admin pueden buscar cualquier localidad
    else:
        consulta_base = "SELECT * FROM localidades WHERE id_usuario = %s AND nombre_localidad LIKE %s"  # Usuarios regulares buscan en sus localidades
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Ajustar los parámetros de la consulta según si el usuario es admin
    parametros = [f"%{nombre_localidad}%"] if es_usuario_admin else [user_id, f"%{nombre_localidad}%"]
    cur.execute(consulta_base, parametros)
    data = cur.fetchall()

    localidadestList = [Localidad(row).to_json() for row in data]

    if localidadestList:
        return jsonify(localidadestList)
    else:
        return jsonify({"message": "No se encontró el localidad buscado"}), 404