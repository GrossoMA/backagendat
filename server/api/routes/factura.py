from api import app
from api.models.factura import Factura
from flask import jsonify, request #permite devolver json
from api.utils import token_required, factura_resource, user_resources, client_resource
from api.db.db import mysql


# # retorna todas las facturas resumidas del usuario solicitado
@app.route('/user/<int:user_id>/facturas', methods=['GET'])
@token_required
@user_resources
def get_all_factura_resumen_by_user_id(user_id):
    fc_list = Factura.get_facturas(user_id)

    if fc_list:
        return jsonify(fc_list)
    else:
        return jsonify({"message": "No se encontraron Facturas relacionadas con el usuario"}),404

# retorna la factura id, del usuario solicitado
@app.route('/user/<int:user_id>/facturas/<int:factura_id>', methods=['GET'])
@token_required
@user_resources
@factura_resource  # Verificamos que la factura solicitada puede ser accedida por el usuario
def get_factura_by_id(user_id, factura_id):
    fc = Factura.get_facturas(user_id,factura_id)

    if fc:
        return jsonify(fc)
    else:
        return jsonify({"message": f"No se encontro Factura nro {factura_id}"}),404
    
    #return jsonify({"message": "ID not found"}), 404

# crea factura. y en caso de exito retorna la factura creada. de lo contrario retorna el error.
@app.route('/user/<int:user_id>/client/<int:client_id>/facturas', methods=['POST'])
@token_required
@user_resources
@client_resource
def crear_fc(user_id,client_id):
    try:       
        datos = request.get_json()         
        
        new_factura = Factura.create_fc(user_id,client_id,datos)

        return jsonify(new_factura),201        
        
    except Exception as e:        
        return jsonify({"message": f"Error en la base de datos: {e}"}), 500

@app.route('/user/<int:user_id>/facturas/<int:factura_id>', methods=['DELETE'])
@token_required
@user_resources
def desactivar_fc(user_id, factura_id):    
    try:
        
        cur = mysql.connection.cursor()
        query = 'UPDATE facturas SET estado = %s WHERE id_factura = %s and id_usuario = %s'
        cur.execute(query, ('2', factura_id,user_id))
        print()
        mysql.connection.commit()
        cur.close()

        if cur.rowcount > 0:  # Verifica si se modificó algún registro en la base de datos
            return jsonify({"message": "FC anulada exitosamente", "success": True}), 200
        else:
            return jsonify({"message": "No se encontró la factura o no se realizó ningún cambio", "success": False}), 404
    except mysql.connector.Error as e:
        return jsonify({"message": f"Error en la base de datos: {e}", "success": False}), 500
    
# Cambia el estado de factura a 3: efectivo 4: debito 5: cheque, solo se podra cambiar a estos estado y debera estar en estado 1
@app.route('/user/<int:user_id>/facturas/<int:factura_id>', methods=['PUT'])
@token_required
@user_resources
@factura_resource
def cobrar_fc(user_id,factura_id):
    try:       
        datos = request.get_json()         
        print(datos)
        fc_cobrada,msj,codigo = Factura.cobrar_factura(user_id,factura_id,datos)
        if fc_cobrada:
            return jsonify(fc_cobrada),codigo        
        return jsonify({"message": msj}), codigo
        
    except Exception as e:        
        return jsonify({"message": f"Error en la base de datos: {e}"}), 500
 