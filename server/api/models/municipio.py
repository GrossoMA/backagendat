class Municipio:
    def __init__(self, row):
        self._id_municipio = row['id_municipio']
        self._nombre_municipio = row['nombre_municipio']

    @property
    def id_municipio(self):
        return self._id_municipio

    @property
    def nombre_municipio(self):
        return self._nombre_municipio

    def to_json(self):
        """
        Convierte el objeto a un diccionario para su fácil serialización a JSON.
        """
        return {
            'id_municipio': self._id_municipio,
            'nombre_municipio': self._nombre_municipio
        }