from api import app
from flask_mysqldb import MySQL
from flask import Flask, request, render_template


app.config['MYSQL_HOST'] = 'grosso4le.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'grosso4le'
app.config['MYSQL_PASSWORD'] ='LoreIsab3947'
app.config['MYSQL_DB'] = 'grosso4le$db_agenda_turistica'
# Límite máximo de contenido a 2 MB
app.config['MAX_CONTENT_LENGTH'] =  8 * 1024 * 1024  # 2 MB en bytes
mysql = MySQL(app)

class DBError(Exception):
    def __init__(self, message, query):
        self.message = message
        self.query = query
        super().__init__(self.message)

