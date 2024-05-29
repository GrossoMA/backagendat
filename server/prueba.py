from flask import Flask, request, render_template
from flask_mysqldb import MySQL


application = Flask(__name__)

application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'aleadmin'
application.config['MYSQL_PASSWORD'] = '123456'
application.config['MYSQL_DB'] = 'db_agenda_turistica'

mysql = MySQL(application)

@application.route('/')
def hello():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios u inner join municipios m on m.id_municipio = u.id_municipio')
    data = cursor.fetchall()
    cursor.close()

    return str(data)

if __name__ == '__main__':
    application.run(debug=True,port=4500)