import os
import uuid
from api import app
from api.models.eventos import Eventos
from flask import jsonify, request #permite devolver json
from werkzeug.utils import secure_filename
from api.utils import token_required, client_resource, user_resources,evento_resource
from api.db.db import mysql
import json

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'public', 'imgeventos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# retorna todos los eventos del usuario solicitado
@app.route('/user/<int:user_id>/eventos', methods = ['GET'])
@token_required
@user_resources
def get_all_eventos_by_user_id(user_id):
    # print("eventos !!!",user_id)
    cur = mysql.connection.cursor()
    cur.execute('''
    SELECT e.*, m.nombre_municipio as nombre_municipio, l.nombre_localidad as nombre_localidad
    FROM eventos e
    JOIN municipios m ON e.id_municipio = m.id_municipio
    JOIN localidades l ON e.id_localidad = l.id_localidad
    WHERE e.id_usuario = {0}
    order by
    CASE
    WHEN e.fecha_inicio IS NULL THEN 1
    ELSE 0
    END,
    e.fecha_inicio asc ,m.nombre_municipio,l.nombre_localidad
'''.format(user_id))
    data = cur.fetchall()
    eventotList = []
    for row in data:
        objEvento = Eventos(row)
        eventotList.append(objEvento.to_json())
    if (len(eventotList) > 0):
        return jsonify(eventotList)
    return jsonify({"messaje": "No se encontraron eventos"})

# retorna todos los eventos del usuario solicitado
@app.route('/user/<int:user_id>/eventos/<int:evento_id>', methods = ['GET'])
@token_required
@user_resources
def get_eventos_by_id(user_id,evento_id):
    # print("eventos !!!",user_id)
    cur = mysql.connection.cursor()
    cur.execute('''
    SELECT e.*, m.nombre_municipio as nombre_municipio, l.nombre_localidad as nombre_localidad
    FROM eventos e
    JOIN municipios m ON e.id_municipio = m.id_municipio
    JOIN localidades l ON e.id_localidad = l.id_localidad
    WHERE e.id_evento = {0}
'''.format(evento_id))
    row = cur.fetchone()
    if row:
        objEvento = Eventos(row)
        return jsonify(objEvento.to_json())

    return jsonify({"mensaje": "No se encontraron eventos"})


    # eventotList = []
    # for row in data:
    #     objEvento = Eventos(row)
    #     eventotList.append(objEvento.to_json())
    # if (len(eventotList) > 0):
    #     return jsonify(eventotList)
    # return jsonify({"messaje": "No se encontraron eventos"})


# Función para verificar la extensión del archivo
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Función para generar un string aleatorio
def generate_random_string():
    return str(uuid.uuid4())

#CREAR UN NUEVO Evento
@app.route('/user/<int:user_id>/eventos', methods=['POST'])
@token_required
@user_resources
def create_evento(user_id):
    print("---insertando evento")
    try:
        CAMPOS_REQUERIDOS = ['nombre_evento', 'id_municipio', 'id_localidad', 'direccion', 'fecha_inicio', 'mes_estimado', 'hora','id_tipo_evento','descripcion','palabras_claves','id_estado']

        # Captura los datos en formato JSON
        data_json = request.get_json()
        print("--> JSON:", data_json)


        print("----------")
        # Convierte el campo de palabras clave de JSON a lista
        # (si no es una lista ya)
        if 'palabras_claves' in data_json and not isinstance(data_json['palabras_claves'], list):
            data_json['palabras_claves'] = json.loads(data_json['palabras_claves'])
        print("----------despues de palabrasclaves")
        # Encuentra los campos que faltan
        campos_faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in data_json]
        if campos_faltantes:
            # Devuelve un mensaje con los campos faltantes
            return jsonify({"message": "Faltan campos en la solicitud", "campos_faltantes": campos_faltantes}), 400
        print("----------despues de campos faltantes")
        
         # Se comprueban que los campos estén completos
        if not data_json or not all(campo in data_json for campo in CAMPOS_REQUERIDOS): 
            return jsonify({"message": "Faltan campos en la solicitud", "campos_faltantes": CAMPOS_REQUERIDOS}), 400
        print("----------despues de campos requeridos")
        
        # Crea una instancia de Cliente
        new_evento = {
            'nombre_evento':data_json['nombre_evento'],
            'id_municipio':data_json['id_municipio'],
            'id_localidad':data_json['id_localidad'],
            'direccion':data_json['direccion'],
            'fecha_inicio':data_json['fecha_inicio'],
            'mes_estimado':data_json['mes_estimado'],
            'hora':data_json['hora'],
            'id_tipo_evento':data_json['id_tipo_evento'],
            'descripcion':data_json['descripcion'],
            'palabras_claves': json.dumps(data_json['palabras_claves']),
            'id_estado':data_json['id_estado'],
            'img1': data_json.get('img1', None),
            'img2': data_json.get('img2', None),
            'img3': data_json.get('img3', None)
        }
        print("----------despues de nuevo evento")
        
        # --------------------------------

        # # Captura los datos del formulario
        # data = request.form.to_dict()
        # palabras_claves = request.form.get('palabras_claves')
        # print("data")
        # print(data)

        # # Convierte el campo de palabras clave de JSON a lista
        # if palabras_claves:
        #     data['palabras_claves'] = json.loads(palabras_claves)
        # # Encuentra los campos que faltan
        # print("----------buscando campos faltantes")
        # campos_faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in data]
        # print("campos_faltantes",campos_faltantes)

        # if campos_faltantes:
        #     # Devuelve un mensaje con los campos faltantes
        #     print("return campos faltantes", campos_faltantes)
        #     return jsonify({"message": "Faltan campos en la solicitud", "campos_faltantes": campos_faltantes}), 400

        # # Se comprueban que los campos estén completos
        # if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS): 
        #         print("return comprobar estan todos los campos", campos_faltantes)          
        #         return jsonify({"message"}), 400
        
        # Manejar las imágenes si están presentes y son válidas
        print("----------despues de imagenm")
        image_fields = ['img1', 'img2', 'img3']
        for field in image_fields:
            if field in request.files:
                image = request.files[field]
                if image and allowed_file(image.filename):
                    random_string = generate_random_string()
                    filename = secure_filename(f"{field}_{random_string}.{image.filename.rsplit('.', 1)[1].lower()}")
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    data_json[field] = filename
                else:
                    data_json[field] = None
            else:
                data_json[field] = None
        print("----------despues de imagenes")

        # Aca TODO ver la posibilidad de controlar eventdos duplicados
        # cur = mysql.connection.cursor()
        # cur.execute('SELECT COUNT(*) FROM eventos WHERE cuit_cuil = %s OR dni = %s OR email = %s', (data['cuitCuil'],  data['dni'], data['email']))
        # count = cur.fetchone()[0]
        # cur = mysql.connection.cursor()
        # ---------------------------------------------------------------- esto se puede mover

        # # Si alguno de los valores ya existe, abortar la actualización
        # if count > 0:
        #     print('aca')
        #     return jsonify({"message": "Al menos uno de los valores ya existe en la tabla clientes"}),406


        # Crea una instancia de Cliente

        # new_evento = {
        #     'nombre_evento':data['nombre_evento'],
        #     'id_municipio':data['id_municipio'],
        #     'id_localidad':data['id_localidad'],
        #     'direccion':data['direccion'],
        #     'fecha_inicio':data['fecha_inicio'],
        #     'mes_estimado':data['mes_estimado'],
        #     'hora':data['hora'],
        #     'id_tipo_evento':data['id_tipo_evento'],
        #     'descripcion':data['descripcion'],
        #     'palabras_claves': json.dumps(data['palabras_claves']),
        #     'id_estado':data['id_estado'],
        #     'img1': data['img1'],
        #     'img2': data['img2'],
        #     'img3': data['img3']
        # }

        # Conecta con la base de datos
        cur = mysql.connection.cursor()

        # Inserta el evento en la base de datos
        consulta = '''INSERT INTO eventos (nombre_evento, id_usuario, id_municipio, id_localidad, direccion, fecha_inicio, mes_estimado, hora, id_tipo_evento, descripcion, palabras_claves, id_estado, img1, img2, img3)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        valores = (new_evento['nombre_evento'], user_id, new_evento['id_municipio'],
                   new_evento['id_localidad'], new_evento['direccion'], new_evento['fecha_inicio'], new_evento['mes_estimado'],
                   new_evento['hora'], new_evento['id_tipo_evento'], new_evento['descripcion'], new_evento['palabras_claves'], new_evento['id_estado'], new_evento['img1'], new_evento['img2'], new_evento['img3'])
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Evento creado exitosamente"}), 201

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        print("error:", str(e))
        return jsonify({"message": "Evento no agregado"}), 500


#ACTUALIZAR Eventos
@app.route('/user/<int:user_id>/eventos/<int:evento_id>', methods=['PUT'])
@token_required
@user_resources
@evento_resource
def update_evento(user_id, evento_id):
    try:
        CAMPOS_REQUERIDOS = ['nombre_evento', 'id_municipio', 'id_localidad', 'direccion', 'fecha_inicio', 'mes_estimado', 'hora','id_tipo_evento','descripcion','palabras_claves','id_estado']

        # Captura los datos en formato JSON
        data = request.get_json()

        # comprobamos si se proporcionaron los datos necesarios
        if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS):
            return jsonify({"message": "Datos incompletos"}), 400

        # ----------------------------------------------------------------
        # Verificar si los valores de cuitCuil, dni y email ya existen en la tabla clientes
        # Construye la consulta SQL
        query = '''SELECT COUNT(*) FROM eventos WHERE
                (nombre_evento = %s AND id_municipio = %s AND id_localidad = %s)
                AND id_evento != %s'''
        params = (data['nombre_evento'], data['id_municipio'], data['id_localidad'], evento_id)
        # Imprime la consulta SQL y sus parámetros para depuración
        # print("Ejecutando consulta SQL:", query)
        print("Con parámetros:", params)

        # Ejecuta la consulta
        cur = mysql.connection.cursor()
        cur.execute(query, params)
        count = cur.fetchone()[0]
        cur = mysql.connection.cursor()
        # ---------------------------------------------------------------- esto se puede mover

        # Si alguno de los valores ya existe, abortar la actualización
        if count > 0:
            # print('aca')
            return jsonify({"message": "Al menos uno de los valores ya existe en la tabla eventos"}),406

        # Actualiza el evento en la base de datos
        consulta = '''
        UPDATE eventos
        SET
            nombre_evento = %s,
            id_municipio = %s,
            id_localidad = %s,
            direccion = %s,
            fecha_inicio = %s,
            mes_estimado = %s,
            hora = %s,
            id_tipo_evento = %s,
            descripcion = %s,
            palabras_claves = %s,
            id_estado = %s
        WHERE
            id_evento = %s AND
            id_usuario = %s
        '''

        valores = (
            data['nombre_evento'],
            data['id_municipio'],
            data['id_localidad'],
            data['direccion'],
            data['fecha_inicio'],
            data['mes_estimado'],
            data['hora'],
            data['id_tipo_evento'],
            data['descripcion'],
            data['palabras_claves'],
            data['id_estado'],
            evento_id,
            user_id
        )
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Evento actualizado exitosamente"}), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        print("error:", str(e))
        return jsonify({"message": "Datos no actualizados"}), 500

# Eliminar un evento
@app.route('/user/<int:user_id>/eventos/<int:evento_id>', methods=['DELETE'])
@token_required
@user_resources
@evento_resource
def delete_evento(user_id, evento_id):
    # Agregar un campo en la tabla de la DB clientes llamado estado (inactivo = borrado, activo = disponible)
    try:
        # Conecta con la base de datos
        cur = mysql.connection.cursor()

        # Elimina el cliente de la base de datos
        consulta = 'UPDATE eventos SET id_estado = %s WHERE id_evento = %s AND id_usuario = %s'
        valores = (0,evento_id, user_id)
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Evento eliminado exitosamente"}), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        return jsonify({"message": "Evento no eliminado"}), 500