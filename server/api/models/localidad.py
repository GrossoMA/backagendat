class Localidad:
    def __init__(self, row):
        self._id_localidad = row['id_localidad']
        self._nombre_localidad = row['nombre_localidad']
        self._id_municipio = row['id_municipio']

    @property
    def id_localidad(self):
        return self._id_localidad

    @property
    def nombre_localidad(self):
        return self._nombre_localidad

    @property
    def id_municipio(self):
        return self._id_municipio

    def to_json(self):
        """
        Convierte el objeto a un diccionario para su fácil serialización a JSON.
        """
        return {
            'id_localidad': self._id_localidad,
            'nombre_localidad': self._nombre_localidad,
            'id_municipio': self._id_municipio
        }
