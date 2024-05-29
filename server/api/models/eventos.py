class Eventos:
    def __init__(self, row):        
        self._id_evento = row[0]
        self._nombre_evento = row[1]
        self._id_usuario = row[2]
        self._id_municipio = row[3]        
        self._id_localidad = row[4]
        self._direccion = row[5]
        self._fecha_inicio = row[6]
        self._mes_estimado = row[7]
        self._hora = row[8]
        self._tipo_evento = row[9]
        self._descripcion = row[10]
        # self._palabras_claves = row[11]
        self._palabras_claves = row[11] if row[11] else [] 
        self._id_estado = row[12]
        self._img1 = row[13]
        self._img2 = row[14]
        self._img3 = row[15]
        self._nombre_municipio = row[16]
        self._nombre_localidad = row[17]
    
    def to_json(self):
        return {
            "id_evento": self._id_evento,
            "nombre_evento": self._nombre_evento,
            "id_usuario": self._id_usuario,
            "id_municipio": self._id_municipio,            
            "id_localidad": self._id_localidad,
            "direccion": self._direccion,
            "fecha_inicio": self._fecha_inicio,
            "mes_estimado": self._mes_estimado,
            "hora": self._hora,
            "id_tipo_evento": self._tipo_evento,
            "descripcion": self._descripcion,
            # "palabras_claves": self._palabras_claves,
            "palabras_claves": self._palabras_claves if self._palabras_claves else [],  # Transforma [] en ''
            "id_estado": self._id_estado,
            "img1": self._img1,
            "img2": self._img2,
            "img3": self._img3,
            "nombre_municipio": self._nombre_municipio,
            "nombre_localidad": self._nombre_localidad,
        }