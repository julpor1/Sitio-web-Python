#APLICACION CUERPO 
from flask import Flask
from flask import render_template,request,redirect,flash,session
from flaskext.mysql import MySQL
from datetime import datetime
from flask import send_from_directory
import os
app = Flask(__name__)#Creo la aplicacion
app.secret_key = "Julian" #Llave secreta para el uso de mensajes y sesiones
#Conexion entre la app y la base de datos
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sitio'
mysql.init_app(app)



@app.route("/") 
def index():
    return render_template("sitio/index.html")


@app.route('/img/<imagen>')
def imagenes(imagen):
    return send_from_directory(os.path.join("templates/sitio/img"),imagen)

@app.route('/css/<estilos>')
def css_estilos(estilos):
    return send_from_directory(os.path.join("templates/sitio/css"),estilos)


@app.route('/libros')
def libros():
    sql = 'SELECT * FROM `libros` '
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    datos = cursor.fetchall()
    conn.commit()
    return render_template("sitio/libros.html",datos = datos)

@app.route('/nosotros')
def nosotros():
    return render_template("sitio/nosotros.html")

@app.route('/admin')
def admin_index():
    if not 'login' in session:
        flash("Accion restringida")
        return redirect("/login")
    return render_template("admin/index.html")

@app.route('/admin/login')
def login():
    return render_template("admin/login.html")

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        flash("Accion restringida")
        return redirect("/login")

    sql = 'SELECT * FROM `libros` '
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    datos = cursor.fetchall()
    conn.commit()
    return render_template("admin/libros.html",datos = datos)
    


@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        flash("Accion restringida")
        return redirect("/login")

    nombre = request.form['txtNombre']
    url = request.form['txtURL']
    archivo = request.files['txtImagen']

    tiempo = datetime.now()
    horaActual = tiempo.strftime("%Y%H%M%S")

    if archivo.filename != " ":
        nuevoNombre = horaActual+"_"+ archivo.filename
        archivo.save("templates/sitio/img/"+nuevoNombre)

    print(horaActual)

    sql = 'INSERT INTO `libros`(nombre,imagen,url) VALUES (%s,%s,%s)'
    datos = (nombre,nuevoNombre,url)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect("/admin/libros")
    
@app.route('/delete/libros/<int:id>')
def delete_libro(id):

    if not 'login' in session:
        flash("Accion restringida")
        return redirect("/login")

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT imagen FROM `libros` WHERE id = {id}")
    dato = cursor.fetchall()
    conn.commit()

    if os.path.exists("templates/sitio/img/"+dato[0][0]):
        os.remove("templates/sitio/img/"+dato[0][0])



    sql = f'DELETE FROM `libros` WHERE id = {id} '
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

    return redirect("/admin/libros")

@app.route('/login')
def logeo():
    if 'login' in session:
        return redirect("/admin")
    return render_template("admin/login.html")


@app.route('/login/validar', methods=['POST'])
def validar():
    usuario = request.form['txtUsuario']
    contraseña = request.form['txtPassword']

    if usuario == "" or contraseña == "":
        flash("Usuario o contraseña sin digitar")
        return redirect("/login")

    # sql = f"INSERT INTO `usuarios`(user,password) VALUES ('{usuario}','{contraseña}')"
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # cursor.execute(sql)
    # conn.commit() 

    sql = f"SELECT * FROM `usuarios` WHERE password = '{contraseña}' AND user = '{usuario}'"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    datos = cursor.fetchall()
    print(datos)
    conn.commit()

    if len(datos) == 0:
        flash("Usuario o contraseña incorrectos")
        return redirect("/login")

    #Creacion de variables de sesion
    session['login'] = True 
    session['usuario'] = datos[0][1]
    return redirect("/admin")

@app.route('/admin/cerrar')
def cerrar_sesion():
    session.clear() #Destruir sesiones 
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True) #Corriendo Aplicacion