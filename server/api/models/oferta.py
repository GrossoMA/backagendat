#Se llama oferta al producto o servicio
class Oferta():
    def __init__(self, row):
        self._id_oferta = row[0]
        self._nombre = row[1]
        self._tipo = row[2]
        self._descripcion = row[3]
        self._precio = row[4]
        self._stock = row[5]
        self._disponibilidad = row[6]
        self._id_usuario = row[7]
        self._estado = row[8]
        
    def to_json(self):
        return {
            "id_oferta": self._id_oferta,
            "nombre": self._nombre,
            "tipo": self._tipo,
            "descripcion": self._descripcion,
            "precio": self._precio,
            "stock": self._stock,
            "disponibilidad": self._disponibilidad,
            "id_usuario": self._id_usuario,
            "estado": self._estado
        }

################################################################
'''
considerar una funcion para manipular el stock y la disponibilidad

Agregue el campo id usuario a la tabla ofertas.
Cada prodcuto tiene un stock o disponibilidad.
Cada cliente esta relacionado a un usuario en particular.
y cada producto esta relacionado a un usuario en particular, de similar manera que cliente.
Evalue alternativas para manejar las ofertas y su relacion con usuarios, pero me parece que esta es la mas apropiada
Con respecto a Estado, 
tambien agregue este campo para controlar el delete del producto.
'''