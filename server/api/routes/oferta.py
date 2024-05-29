from api import app
from api.models.oferta import Oferta
from flask import jsonify, request #permite devolver json
from api.utils import token_required, oferta_resource, user_resources
from api.db.db import mysql


# retorna todas las ofertas del usuario solicitado
@app.route('/user/<int:user_id>/oferta', methods = ['GET'])
@token_required
@user_resources
def get_all_oferta_by_user_id(user_id):
    print("ofertas")
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM oferta WHERE id_usuario = {0} AND estado = "A"'.format(user_id))
    data = cur.fetchall()
    ofertaList = []
    for row in data:
        objOferta = Oferta(row)
        ofertaList.append(objOferta.to_json())
    if (len(ofertaList) > 0):    
        return jsonify(ofertaList)
    return jsonify({"messaje": "No se encontraron productos o servicios para ofrecer"})

# retorna la oferta con id dado del usuario solicitado
@app.route('/user/<int:user_id>/oferta/<int:oferta_id>', methods = ['GET'])
@token_required
@user_resources
@oferta_resource # verificamos que la oferta solicitada puede ser accedida x el usuario
def get_oferta_by_id(user_id,oferta_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM oferta WHERE  id_usuario = {0} and  id_oferta = {1}'.format(user_id,oferta_id))
    data = cur.fetchall()    
    # ToDo borrar luego
    print(data)
    if cur.rowcount > 0:
        objOferta = Oferta(data[0])
        return jsonify( objOferta.to_json() )
    return jsonify( {"message": "id not found"} ), 404

@app.route('/user/<int:user_id>/oferta', methods=['POST'])
@token_required
@user_resources
def insertar(user_id):
    try:
        # campos de la tabla necesrios para la insercion
        CAMPOS_REQUERIDOS = ['nombre', 'tipo', 'descripcion', 'precio', 'stock', 'disponibilidad', 'id_usuario','estado']
        # p representa productos s representa servicios
        TIPO_OFERTA = ['P','S']
        # datos json
        datos = request.get_json() 
        
        # comprobamos si estan los datos necesarios    
        if not datos or not all(campo in datos for campo in CAMPOS_REQUERIDOS):
            return jsonify({"message": "Datos incompletos"}), 400

        # extraemos la informacion de los campos
        info_campos = {campo: datos[campo] for campo in CAMPOS_REQUERIDOS}
        
        # verificamos si el user coincide con la informacion del dato recibido 
        if int(info_campos['id_usuario']) != int(user_id):
            return jsonify({"message": "User Incorrecto."}), 401
        
        if info_campos['tipo'] not in TIPO_OFERTA:
            return jsonify({"message": "Datos incorrectos"}), 400
        
        # armamos la query para la inserción en la base de datos
        cur = mysql.connection.cursor()
        consulta = 'INSERT INTO oferta ({}) VALUES ({})'.format(
            ', '.join(info_campos.keys()), ', '.join(['%s'] * len(info_campos))
        )
        valores = tuple(info_campos.values())
        cur.execute(consulta, valores)
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Inserción exitosa"}), 201
    except mysql.connector.Error as e:                        
        return jsonify({"message": f"Error en la base de datos: {e}"}), 500

@app.route('/user/<int:user_id>/oferta/<int:oferta_id>', methods=['DELETE'])
@token_required
@user_resources
@oferta_resource
def desactivar_oferta(user_id, oferta_id):
    try:
        # Comprobamos si la oferta pertenece al usuario
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM oferta WHERE id_oferta = %s AND id_usuario = %s AND estado = "A"', (oferta_id, user_id))
        oferta = cur.fetchone()
        cur.close()

        if not oferta:
            return jsonify({"message": "Oferta no encontrada"}), 404

        print("borrando oferta: ",oferta)
        # Cambiamos el estado de la oferta a inactivo ('I')
        cur = mysql.connection.cursor()
        cur.execute('UPDATE oferta SET estado = %s WHERE id_oferta = %s', ('I', oferta_id))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Oferta desactivada exitosamente"}), 200
    except mysql.connector.Error as e:
        return jsonify({"message": f"Error en la base de datos: {e}"}), 500
    
@app.route('/user/<int:user_id>/oferta/<int:oferta_id>', methods=['PUT'])
@token_required
@user_resources
@oferta_resource
def update_oferta(user_id, oferta_id):
    try:
        # campos que pueden ser actualizados
        CAMPOS_ACTUALIZABLES = ['nombre', 'tipo', 'descripcion', 'precio', 'stock', 'disponibilidad','id_usuario','estado']
        TIPO_OFERTA = ['P','S']

        # datos json
        datos = request.get_json() 
        
        # comprobamos si se proporcionaron los datos necesarios    
        if not datos or not all(campo in datos for campo in CAMPOS_ACTUALIZABLES):
            return jsonify({"message": "Datos incompletos"}), 400

        # extraemos la información de los campos
        info_campos = {campo: datos[campo] for campo in CAMPOS_ACTUALIZABLES}
        
        # verificamos si el tipo es válido
        if info_campos['tipo'] not in TIPO_OFERTA:
            return jsonify({"message": "Tipo de oferta incorrecto"}), 400

        # armamos la query para la actualización en la base de datos
        cur = mysql.connection.cursor()
        consulta = 'UPDATE oferta SET {} WHERE id_oferta = %s AND id_usuario = %s'.format(
            ', '.join([f"{campo} = %s" for campo in info_campos.keys()])
        )
        valores = list(info_campos.values()) + [oferta_id, user_id]
        cur.execute(consulta, valores)
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Actualización exitosa"}), 200

    except mysql.connector.Error as e:
        return jsonify({"message": f"Error en la base de datos: {e}"}), 500

"""
id_oferta int(10) AI PK 
nombre varchar(255) 
tipo char(1) 
descripcion varchar(255) 
precio decimal(2,0) 
stock int(10) 
disponibilidad tinyint(1) 
        
"""