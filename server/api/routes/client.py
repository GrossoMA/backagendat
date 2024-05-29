from api import app
from api.models.client import Client
from flask import jsonify, request #permite devolver json
from api.utils import token_required, client_resource, user_resources
from api.db.db import mysql

# RETORNA LOS DATOS DEL CLIENTE SOLICITADO
@app.route('/user/<int:user_id>/client/<int:client_id>', methods = ['GET'])
@token_required
@user_resources
@client_resource
def get_client_by_id(user_id,client_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes WHERE  id_usuario = {0} and  id_cliente = {1}'.format(user_id,client_id))
    data = cur.fetchall()
    print(cur.rowcount)
    if cur.rowcount > 0:
        objClient = Client(data[0])
        return jsonify( objClient.to_json() )
    return jsonify( {"message": "id not found"} ), 404

# retorna todos los clientes del usuario solicitado
@app.route('/user/<int:user_id>/client', methods = ['GET'])
@token_required
@user_resources
def get_all_clients_by_user_id(user_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM clientes WHERE estado = 1 AND id_usuario = {0}'.format(user_id))
    data = cur.fetchall()
    clientList = []
    for row in data:
        objClient = Client(row)
        clientList.append(objClient.to_json())
    if (len(clientList) > 0):    
        return jsonify(clientList)
    return jsonify({"messaje": "No se encontraron clientes"})

#CREAR UN NUEVO CLIENTE
@app.route('/user/<int:user_id>/client', methods=['POST'])
@token_required
@user_resources
def create_client(user_id):
    try:
        CAMPOS_REQUERIDOS = ['nombre', 'cuitCuil', 'apellido', 'dni', 'domicilio', 'telefono', 'email']
        
        # Captura los datos en formato JSON
        data = request.get_json()
        print(data)

        # Se comprueban que los campos estén completos
        if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS):           
            return jsonify({"message": "Datos incompletos"}), 400

        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM clientes WHERE cuit_cuil = %s OR dni = %s OR email = %s', (data['cuitCuil'],  data['dni'], data['email']))
        count = cur.fetchone()[0]             
        cur = mysql.connection.cursor()      
        # ---------------------------------------------------------------- esto se puede mover

        # Si alguno de los valores ya existe, abortar la actualización
        if count > 0:
            print('aca')
            return jsonify({"message": "Al menos uno de los valores ya existe en la tabla clientes"}),406

        
        # Crea una instancia de Cliente
        new_client = {
            'nombre': data['nombre'],
            'id_usuario': user_id,
            'cuitCuil' : data['cuitCuil'],
            'apellido' : data['apellido'], 
            'dni' : data['dni'],
            'domicilio' : data['domicilio'],
            'telefono' : data['telefono'],
            'email' : data['email'], 
            'estado' : 1
                }        
        
        # Conecta con la base de datos
        cur = mysql.connection.cursor()
        
        # Inserta el cliente en la base de datos
        consulta = 'INSERT INTO clientes (nombre, id_usuario, cuit_cuil, apellido, dni, domicilio, telefono, email, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        valores = (new_client['nombre'], new_client['id_usuario'], new_client['cuitCuil'], 
                   new_client['apellido'], new_client['dni'], new_client['domicilio'], new_client['telefono'],
                   new_client['email'], new_client['estado'])
        print(consulta)
        print(valores)
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()              

        return jsonify({"message": "Cliente creado exitosamente"}), 201

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        print("error:", str(e))
        return jsonify({"message": "Cliente no agregado"}), 500


#ACTUALIZAR CLIENTE
@app.route('/user/<int:user_id>/client/<int:client_id>', methods=['PUT'])
@token_required
@user_resources
@client_resource
def update_client(user_id, client_id):
    try:
        CAMPOS_REQUERIDOS = ['nombre', 'cuitCuil', 'apellido', 'dni', 'domicilio', 'telefono', 'email']

        # Captura los datos en formato JSON
        data = request.get_json()   

        # comprobamos si se proporcionaron los datos necesarios    
        if not data or not all(campo in data for campo in CAMPOS_REQUERIDOS):
            return jsonify({"message": "Datos incompletos"}), 400

        # ----------------------------------------------------------------
        # Verificar si los valores de cuitCuil, dni y email ya existen en la tabla clientes
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(*) FROM clientes WHERE (cuit_cuil = %s OR dni = %s OR email = %s) AND id_cliente != %s', (data['cuitCuil'],  data['dni'], data['email'], client_id))
        count = cur.fetchone()[0]             
        cur = mysql.connection.cursor()      
        # ---------------------------------------------------------------- esto se puede mover

        # Si alguno de los valores ya existe, abortar la actualización
        if count > 0:
            print('aca')
            return jsonify({"message": "Al menos uno de los valores ya existe en la tabla clientes"}),406

        # Actualiza el cliente en la base de datos
        consulta = 'UPDATE clientes SET nombre = %s, cuit_cuil = %s, apellido = %s, dni = %s, domicilio = %s, telefono = %s, email = %s, estado = %s WHERE id_cliente = %s AND id_usuario = %s'
        valores = (data['nombre'], data['cuitCuil'], data['apellido'], data['dni'], data['domicilio'], 
                   data['telefono'], data['email'], 1, client_id, user_id)
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()  
        return jsonify({"message": "Cliente actualizado exitosamente"}), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso  
        print("error:", str(e))     
        return jsonify({"message": "Datos no actualizados"}), 500
    
# Eliminar un cliente
@app.route('/user/<int:user_id>/client/<int:client_id>', methods=['DELETE'])
@token_required
@user_resources
@client_resource
def delete_client(user_id, client_id):
    # Agregar un campo en la tabla de la DB clientes llamado estado (inactivo = borrado, activo = disponible)
    try:
        # Conecta con la base de datos
        cur = mysql.connection.cursor()

        # Elimina el cliente de la base de datos
        consulta = 'UPDATE clientes SET estado = %s WHERE id_cliente = %s AND id_usuario = %s'
        valores = (0,client_id, user_id)
        cur.execute(consulta, valores)

        # Realiza el commit y cierra la conexión
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Cliente eliminado exitosamente"}), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir durante el proceso
        return jsonify({"message": "Cliente no eliminado"}), 500