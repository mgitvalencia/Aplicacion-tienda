from flask import Flask, jsonify, request
import json
import yaml
import argparse
import sqlite3

parser = argparse.ArgumentParser(description="Aplicacion tienda para el Master Full Stack")
parser.add_argument("-s", "--servidor", type=str, default="localhost", required=False, help="Nombre o IP del servidor")
parser.add_argument("-p", "--puerto", type=str, default='5000', required=False , help="Puerto para el servicio API")
parser.add_argument("-c", "--config", type=str, required=True, help="Nombre y ruta del archivo de configuracion")
parser.add_argument("-k", "--key", type=str, required=True, help="API KEY para consumo de almacen")

"""para debugg
parser = argparse.ArgumentParser(description="Aplicacion tienda para el Master Full Stack")
parser.add_argument("-s", "--servidor", type=str, default="localhost", required=False, help="Nombre o IP del servidor")
parser.add_argument("-p", "--puerto", type=str, default='5000', required=False , help="Puerto para el servicio API")
parser.add_argument("-c", "--config", type=str, default='tienda.yaml', required=False, help="Nombre y ruta del archivo de configuracion")
parser.add_argument("-k", "--key", type=str, default='KEY', required=False, help="API KEY para consumo de almacen")
"""

#Captura de parametros en variables
args = parser.parse_args()
servidor = args.servidor
puerto = args.puerto
arcConfiguracion = args.config
apiKEY = args.key

#Lectura de configuraciones del archivo yaml
with open(args.config, 'r') as fileConfig:
    try:
        dicConfig = yaml.safe_load(fileConfig)
        dbBaseDatos = dicConfig["basedatos"]["path"]
    except yaml.YAMLError as exc:
        print(exc)
fileConfig.close() 

app = Flask(__name__)

def crearBD():
    # Crear Base de Datos tienda.db    
    con = sqlite3.connect(dbBaseDatos)
    con.commit()
    con.close()

def crearTabla():
    # Crear tabla productos
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()
    try:
        cur.execute('''CREATE TABLE productos
               (codigo text primary key, descripcion text, cantidad real, precio real)''')
        print("Tabla productos creada")       
        cur.execute("INSERT INTO productos VALUES ('PROD-BASE', 'PRODUCTO BASE', 100, 1)")
    except sqlite3.OperationalError:
        print("La tabla productos ya existe")    
    con.commit()
    con.close()

def validaUsuario(usuario, clave):
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()
    resultado = cur.execute('SELECT * FROM usuarios WHERE codigo = ?', (usuario,))
    row = resultado.fetchone()
    if (row == None):
        return jsonify({"error": True, "mensaje": "usuario no existe", "usuario": usuario})
    else:
        if (row[1] != clave):
           return jsonify({"error": True, "mensaje": "clave invalida", "usuario": usuario})
        else:
            return jsonify({"error": False, "mensaje": ""})   
    con.close() 


@app.route('/productos', methods=['GET'])
def leerProductos():
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()

    usuario = request.headers.environ['HTTP_USUARIO']       
    clave = request.headers.environ['HTTP_CLAVE']       
    validacion = validaUsuario(usuario, clave)
    if (validacion.json['error']):
       return jsonify(validacion.json)

    cur.execute('SELECT * FROM productos')
    resultado = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    print(json.dumps(resultado, indent=2, sort_keys=True))
    con.close() 
    return jsonify(resultado)

@app.route('/productos', methods=['POST'])
def crearProducto():
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()

    usuario = request.headers.environ['HTTP_USUARIO']       
    clave = request.headers.environ['HTTP_CLAVE']       
    validacion = validaUsuario(usuario, clave)
    if (validacion.json['error']):
       return jsonify(validacion.json)

    codigo = request.json['codigo']
    descripcion = request.json['descripcion']
    precio = request.json['precio']
    cantidad = request.json['cantidad']
    resultado = cur.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
    if (len(resultado.fetchall()) == 0):
        cur.execute("INSERT INTO productos(codigo, descripcion, precio, cantidad) VALUES (?, ?, ?, ?)", (codigo, descripcion, precio, cantidad))   
        con.commit()
        cur.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
        resultado = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        con.commit()
        con.close()
        return jsonify(resultado)
    else: 
        return jsonify({"Mensaje": "El producto ya existe", "Codigo de Producto": codigo})       
    
@app.route('/productos', methods=['PUT'])
def actualizarProducto():
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()

    usuario = request.headers.environ['HTTP_USUARIO']       
    clave = request.headers.environ['HTTP_CLAVE']       
    validacion = validaUsuario(usuario, clave)
    if (validacion.json['error']):
       return jsonify(validacion.json)

    codigo = request.json['codigo']
    descripcion = request.json['descripcion']
    precio = request.json['precio']
    cantidad = request.json['cantidad']
    resultado = cur.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
    if (len(resultado.fetchall()) != 0):
        cur.execute("UPDATE productos set descripcion = ?, precio = ?, cantidad = ? WHERE codigo = ?", (descripcion, precio, cantidad, codigo))   
        con.commit()
        cur.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
        resultado = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        con.commit()
        con.close()
        return jsonify(resultado)
    else: 
        return jsonify({"Mensaje": "El producto NO existe", "Codigo de Producto": codigo})       

@app.route('/productos', methods=['DELETE'])
def eliminarProducto():
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()

    usuario = request.headers.environ['HTTP_USUARIO']       
    clave = request.headers.environ['HTTP_CLAVE']       
    validacion = validaUsuario(usuario, clave)
    if (validacion.json['error']):
       return jsonify(validacion.json)

    codigo = request.json['codigo']
    resultado = cur.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,))
    if (len(resultado.fetchall()) != 0):
        cur.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))   
        con.commit()
        con.close()
        return jsonify({"Mensaje": "El producto fue eliminado", "Codigo de Producto": codigo})
    else: 
        return jsonify({"Mensaje": "El producto NO existe", "Codigo de Producto": codigo}) 


if __name__ == "__main__":
    print(args)
    crearBD()
    crearTabla()
    app.run(debug=True, host=servidor, port=puerto)


   


