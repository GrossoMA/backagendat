from datetime import datetime
from api.db.db import mysql,DBError 
from flask import jsonify
class Factura():
    # definición del esquema de datos para las facturas
    schema ={
        "id_usuario": int,
        "id_cliente": int,
        "fecha": str,
        "importe_total": float,        
        "estado": int
    }
    # validación de la integridad de los datos
    @staticmethod
    def check_data_schema(data):
        # Verificamos si 'data' es nulo o no es un diccionario        
        if data is None or type(data) != dict:
            return False                
        # Iteramos sobre las claves del esquema de datos de Factura
        for key in Factura.schema:            
            # Verificamos si cada clave está presente en 'data'
            if key not in data:
                # Si falta alguna clave, retornamos False
                return False
            # Si la llave es fecha
            if key == "fecha":                
                # Verificamos si el tipo de dato de la clave coincide con el esquema
                if type(data['fecha']) != Factura.schema["fecha"]:
                    # Si no coincide                    
                    return False
                
                try:
                    # Intentamos convertir la fecha al formato esperado
                    datetime.strptime(data["fecha"], "%Y-%m-%d")
                
                except ValueError:                
                    # Si hay un error en la conversión, la fecha no tiene el formato esperado
                    return False
            # Para las demas llaves que no soy fecha verificamos que coincidan los 
            elif type(data[key]) != Factura.schema[key]:
                return False            
        print("-------*-----------*--------ok hasta aca")
        # Si hemos pasado todas las verificaciones, retornamos True        
        return True
    #  inicialización de una instancia de factura a partir de una fila de datos
    def __init__(self, row):
        self._id_factura = row[0]
        self._id_usuario = row[1]
        self._id_cliente = row[2]
        self._fecha = row[3]
        self._importe = row[4]        
        self._estado = row[5]
    # conversión de la instancia de factura a formato JSON
    def to_json(self):
        return {
            "id": self._id_factura,
            "id_usuario": self._id_usuario,
            "id_cliente": self._id_cliente,
            "fecha": self._fecha,
            "importe": self._importe,            
            "estado": self._estado
        }
    
    @staticmethod
    def update_total_fc(total,id):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE facturas SET importe_total = %s , estado =1 WHERE id_factura = %s",(total,id))
        mysql.connection.commit()        
        if cur.rowcount > 0:
            cur.close()
            return True
        cur.close()
        return False
    
    def insert_registro_fc(info_campos,user_id,client_id):    
        print("Inserting...")    
        curdetalle = mysql.connection.cursor()        
        insert = "INSERT INTO facturas (id_usuario, id_cliente, fecha, importe_total, estado) VALUES (%s,%s,%s,%s,%s)"
        valores = ( info_campos['id_usuario'],info_campos['id_cliente'],info_campos['fecha'],info_campos['importe_total'],info_campos['estado'])
        print("query:")
        print(insert)
        print(valores)
        try:
            curdetalle.execute(insert, valores)            
            mysql.connection.commit()    
            if curdetalle.rowcount > 0:                                                       
                curdetalle.execute("SELECT LAST_INSERT_ID()")   #devuelve el ultimo valor insertado en la tabla SQL             
                res = curdetalle.fetchall()  #todo ver de reemplazar por fetchone()              
                id_last_insert = res[0][0]
                curdetalle.close()  
                print("--------------------------------")
                print("se inserto detalle")
                print("--------------------------------")
                return True, 'Insert OK', id_last_insert
        except Exception as e: #mysql.connector.Error as e:
            print("Error:", e)
        curdetalle.close()
        return False, 'Error insertar Factura', 0
    @staticmethod
    def armar_info_registro_fc(user_id,client_id):
        # Obtener la fecha actual
        fecha_actual = datetime.date(datetime.now())                  
        info_campos = {           
        "id_usuario": user_id,
        "id_cliente": client_id,
        "fecha": fecha_actual,
        "importe_total": 0.00,            
        "estado": 0 # Estado previo a ser creada de forma correcta
        }
        return info_campos
    
    def create_fc(user_id,client_id,data_fc):
        print("Creaando fc...")
        # Verificamos si 'data_fc' está vacío o no es un diccionario
        if not data_fc or not isinstance(data_fc, dict):
            raise ValueError("El JSON recibido está vacío o no es un diccionario")       
        
        # Verificamos si 'data_fc' contiene las clave 'detalle_fc'
        if 'detalle_fc' not in data_fc:            
            raise ValueError("El JSON no contiene las seccion 'detalle_fc'")
        # Obtenemos 'detalle_fc' del JSON recibido        
        data_detalle = data_fc["detalle_fc"]
                
        nueva_info_fc = None          
        # verificamos los datos                
        if ElementoDetalleFactura.check_data_schema(user_id,data_detalle):             
            info_registro_fc = Factura.armar_info_registro_fc(user_id,client_id)            
            result_insert, msj, ultimo_id = Factura.insert_registro_fc(info_registro_fc, user_id,client_id)                                
            if result_insert: 
                #---------------------------------------------------------------- 
                print(msj)                                                                  
                nueva_info_fc = {'id_factura': ultimo_id}
                # agregamos el resto de la información al encabezado
                nueva_info_fc.update(info_registro_fc)     
                #----------------------------------------------------------------         
                # procedemos a insertar el detalle de la factura en la tabla correspondiente  y calculamos el total de la factura
                detalle,total_fc = ElementoDetalleFactura.insertar_detalle(ultimo_id, data_detalle)
                # con el valor calculado procedemos a actualizar el registro correspondiente a la factura creada
                Factura.update_total_fc(total_fc,ultimo_id)
                #----------------------------------------------------------------
                # actualizamos el valor calculado para retornar al frontend
                nueva_info_fc['importe_total']=total_fc     
                #----------------------------------------------------------------           
                # actualizamos el stock de la tabla oferta                
                for elemento in detalle:
                    if not Factura.update_stock_oferta(elemento[2], elemento[4]):
                        print("error al actualizar el stock")
                        return 'Error al actualizar stock'  
                fc_nueva = Factura.get_facturas(user_id, ultimo_id)              
                return fc_nueva               
            raise DBError("Error al insertar datos", nueva_info_fc)
        raise TypeError("Error tipos")
    
    def cobrar_factura(user_id,factura_id,data_fc):
        print("cobrando fc")
        # Verificamos si 'data_fc' está vacío o no es un diccionario
        if not data_fc or not isinstance(data_fc, dict):
            raise ValueError("El JSON recibido está vacío o no es un diccionario")       

        # Verificamos si 'data_fc' contiene las clave 'detalle_fc'
        if 'forma_pago' not in data_fc:            
            raise ValueError("El JSON no contiene las seccion 'detalle_fc'")

        # Obtenemos 'detalle_fc' del JSON recibido        
        forma_de_pago = data_fc["forma_pago"]
        result,msj,codigo = Factura.actualizar_cobro(user_id,factura_id,forma_de_pago)

        if result:
            fc = Factura.get_facturas(user_id, factura_id)              
            return fc, msj,codigo        
        return result,msj,codigo
        
    @staticmethod
    def update_stock_oferta(id_oferta, cantidad_vendida):
        print("update stock oferta")
        print(id_oferta,cantidad_vendida)
        # ----------------------------------------------------------------
        cur = mysql.connection.cursor()
        cur.execute("SELECT stock, tipo FROM oferta WHERE id_oferta = %s", (id_oferta,))
        stock_actual_y_tipo = cur.fetchone()

        if stock_actual_y_tipo:
            stock, tipo = stock_actual_y_tipo  # Desempaquetar los valores
            print("Stock:", stock)
            print("Tipo:", tipo)
            if tipo == 'P' or tipo =='p':
                stock = stock - cantidad_vendida
                cur.execute("UPDATE oferta SET stock = %s WHERE id_oferta = %s",(stock,id_oferta))
                mysql.connection.commit()
                print("estamos locos")
                if cur.rowcount > 0:
                    cur.close()
                    return True

        else:
            print("Oferta no encontrada")
        cur.close()
        return False
    @staticmethod
    def actualizar_cobro(user_id,factura_id,forma_de_pago):
        print("update cobro")        
        # ----------------------------------------------------------------
        if int(forma_de_pago) not in [3,4,5]:# todo reemplazar por constantes
            msj_error = "Forma de pago invalida"
            codigo = 400
            return False,msj_error,codigo
        print("aca",(forma_de_pago,user_id,factura_id,1))


        cur = mysql.connection.cursor()
        query = "UPDATE facturas SET estado = %s WHERE id_usuario = %s AND id_factura = %s AND estado = %s "
        pendiente_de_pago = 1
        esta_en_condiciones = cur.execute(query, (forma_de_pago,user_id,factura_id,pendiente_de_pago))# todo reemplazar por constantes por ahora solo cuando este en 1

        mysql.connection.commit()
        cur.close()       

        if esta_en_condiciones > 0:        
            codigo =201   
            msj = "Registro exitoso."
            return True, msj,codigo
        codigo = 403
        msj_error = "No se pudo realizar registracion de cobro. Verifique el estado FC."
        return False,msj_error,codigo
    
    @staticmethod
    def get_facturas(user_id, factura_id=0):
        cur = mysql.connection.cursor()
        query = '''
            SELECT f.id_factura, f.id_usuario, u.nombre, u.apellido,
            f.id_cliente, cl.nombre, cl.apellido, cl.cuit_cuil, cl.domicilio, cl.telefono, cl.email,
            f.fecha, f.importe_total, f.estado, df.id_oferta, o.nombre, df.importe, df.cantidad, round(df.importe * df.cantidad, 2) as subtotal, o.tipo
            FROM facturas f
            INNER JOIN detalle_facturas df ON df.id_factura = f.id_factura
            INNER JOIN oferta o ON o.id_oferta = df.id_oferta
            INNER JOIN usuarios u ON u.id_usuario = f.id_usuario
            INNER JOIN clientes cl ON cl.id_cliente = f.id_cliente
            WHERE f.id_usuario = %s AND f.estado != 2
        '''
        if factura_id:
            query += ' AND f.id_factura = %s'
            cur.execute(query, (user_id, factura_id))
        else:
            cur.execute(query, (user_id,))

        
        data = cur.fetchall()        
        cur.close()

        facturas_list = Factura.generar_lista_facturas(data)

        return facturas_list
    
    @staticmethod
    def generar_lista_facturas(data):
        facturas_dict = {}

        for row in data:
            id_factura = row[0]

            if id_factura not in facturas_dict:
                # Información de encabezado para una nueva factura
                facturas_dict[id_factura] = {
                    "encabezado": {
                        "id_factura": row[0],
                        "id_usuario": row[1],
                        "nombre_usuario": row[2],
                        "apellido_usuario": row[3],
                        "id_cliente": row[4],
                        "nombre_cliente": row[5],
                        "apellido_cliente": row[6],
                        "cuit_cuil": row[7],
                        "domicilio": row[8],
                        "telefono": row[9],
                        "email": row[10],
                        "fecha": str(row[11]),
                        "importe_total": row[12],
                        "estado":row[13]
                    },
                    "detalle": []  # Detalles para esta factura
                }

            # Detalle para la factura actual
            detalle = {
                
                "id_oferta": row[-6],
                "nombre_oferta": row[-5],
                "importe": row[-4],
                "cantidad": row[-3],
                "subtotal": row[-2],
                "tipo": row[-1]
            }

            # Agrega el detalle a la lista correspondiente a la factura actual
            facturas_dict[id_factura]["detalle"].append(detalle)

        # Convertir el diccionario a una lista de facturas
        facturas_list = [{"encabezado": v["encabezado"], "detalle": v["detalle"]} for v in facturas_dict.values()]
        return facturas_list
    
class ElementoDetalleFactura:
    schema = {        
        "id_oferta":int,   
        "importe":float, 
        "cantidad": int
    }
    @staticmethod
    def check_data_schema(user_id,elementos):
        # Verificamos si la lista de elementos está vacía
        if not elementos:
            return False, "Lista vacía"  # Retornamos False y mensaje de lista vacía
        # print("lista de elementos", elementos)
        try:            
            with mysql.connection.cursor() as cursor:            
                # Iteramos sobre la lista
                for elemento in elementos:                    
                    # Verificamos para cada 'elemento' es nulo o no es un diccionario
                    if elemento is None or not isinstance(elemento, dict):                        
                        return False, "Elemento inválido"  # Retornamos False y mensaje de elemento inválido
                    
                    # Iteramos sobre las claves del esquema de detalla factura
                    #for key in ElementoDetalleFactura.schema:
                    for key in ["id_oferta", "cantidad"]:
                        # Verificamos si cada clave está presente en 'elemento'
                        if key not in elemento:
                            # Si falta alguna clave, retornamos False                            
                            return False, f"Falta '{key}' en el elemento"  # Retornamos False y mensaje de clave faltante
                        
                        # Verificamos que coincidan los tipos en el elemento con los tipos en schema
                        if type(elemento[key]) != ElementoDetalleFactura.schema[key]:                                
                            return False, f"Tipo incorrecto para '{key}' en el elemento"  # Retornamos False y mensaje de tipo incorrecto
                    
                        
                        # Consultamos que cada elemento tenga stock / servicio disponible
                        query = """
                            SELECT 
                                COUNT(*) 
                            FROM 
                                oferta 
                            WHERE 
                                id_usuario = %s 
                                AND estado = 'A' 
                                AND id_oferta = %s
                                AND IF(
                                    (SELECT tipo FROM oferta WHERE id_oferta = %s) = 'P',
                                    stock >= %s, 
                                    disponibilidad = %s
                                ) 
                                
                        """
                        # Ejecutamos la consulta con los parámetros correspondientes
                        
                        cursor.execute(query, (
                            user_id,
                            elemento["id_oferta"],
                            elemento["id_oferta"],
                            elemento["cantidad"],
                            elemento["cantidad"]                        
                        ))                        
                        # Obtenemos el resultado de la consulta
                        result = cursor.fetchone()                        
                        # Verificamos si el resultado es mayor a 0
                        if result[0] <= 0:                            
                            return False, "No hay disponibilidad o el producto no pertenece al usuario"
        except Exception as e:
            print(e)

        finally:
            cursor.close()
        
        # Si todas las validaciones pasan para todos los elementos, retornamos True
        return True, "Todos los elementos son válidos"


    #tipo de dato de la lista de facturas
    def __init__(self, row):
        self._id_detalle_factura = row[0]
        self._id_factura = row[1]
        self._id_oferta = row[2]        
        self._importe = row[3]        
        self._cantidad = row[4]
    def to_json(self):
        return {
            "id_detalle": self._id_detalle_factura,
            "id_factura": self._id_factura,
            "id_oferta": self._id_oferta,            
            "importe": self._importe,
            "cantidad": self._cantidad            
        }
    @staticmethod
    def insertar_detalle(id_factura, datos_detalle):    
        # ya verificamos con check_data_schema, ya existe datos_detalle y son correctos
        #campos_detalle = ["id_factura", "id_oferta", "detalle", "importe", "cantidad"]
        # ahora armamos los campos de la tabla
        campos_detalle = ["id_factura"] + list(ElementoDetalleFactura.schema.keys())
        # preparamos la query
        cur = mysql.connection.cursor()
        
        print("campos detalle:",campos_detalle)
       
        # Creamos una lista de tuplas con los valores a insertar
        
        valores_detalle = []
        try:
            for detalle in datos_detalle:   
                print('detalle: ',detalle)             
                query = """
                            SELECT 
                                precio
                            FROM 
                                oferta 
                            WHERE                             
                                id_oferta = %s                            
                        """
                cur.execute(query, (detalle["id_oferta"],))                
                importe = cur.fetchone()                
                detalle["importe"] = importe[0] if importe else 0
                valores_detalle.append((
                    id_factura,
                    detalle["id_oferta"],
                    detalle["importe"],
                    detalle["cantidad"]
                ))
        except Exception as e:
            print("Error:", e)

        

        # Insertar los datos del detalle
        consulta = 'INSERT INTO detalle_facturas ({}) VALUES ({})'.format(
            ', '.join(campos_detalle),
            ', '.join(['%s'] * len(campos_detalle))
        )        
        cur.executemany(consulta, valores_detalle)
        mysql.connection.commit()
        
        # Verificar si se insertaron los datos
        if cur.rowcount > 0:
            # Obtener los registros recién insertados
            consulta_select = 'SELECT * FROM detalle_facturas WHERE id_factura = %s'
            
            cur.execute(consulta_select, (id_factura,))
            registros_creados = cur.fetchall()
            calcular_importe = 'SELECT sum(cantidad * importe) FROM detalle_facturas WHERE id_factura = %s'
            cur.execute(calcular_importe, (id_factura,))
            total_importe = cur.fetchone()
            cur.close()
            return registros_creados,total_importe  # Retornamos los registros creados y el total de la factura
        else:
            cur.close()
            return [], 0 # No se insertaron registros, retornar lista vacía
