class User():
    def __init__(self, row):        
        self._id_usuario= row[0]        
        self._nombreusuario= row[1]   
        self._contrasenia = row[2]             
        self._nombre = row[3]
        self._apellido = row[4]
        self._dni = row[5]
        self._domicilio = row[6]
        self._telefono = row[7]
        self._email = row[8]
        
    
    def to_json(self):
        return {
            "id_usuario": self._id_usuario,  
            "nombreusuario": self._nombreusuario,  
            "contrasenia": self._contrasenia,            
            "nombre": self._nombre,
            "apellido": self._apellido,
            "dni": self._dni,
            "domicilio": self._domicilio,
            "telefono": self._telefono,
            "email": self._email,
    }