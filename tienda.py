from flask import Flask, jsonify
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

args = parser.parse_args()
servidor = args.servidor
puerto = args.puerto
arcConfiguracion = args.config
apiKEY = args.key

with open(args.config, 'r') as fileConfig:
    try:
        dicConfig = yaml.safe_load(fileConfig)
        dbBaseDatos = dicConfig["basedatos"]["path"]
    except yaml.YAMLError as exc:
        print(exc)
fileConfig.close() 

app = Flask(__name__)

def crearBD(dbBaseDatos):
    # Crear Base de Datos tienda.db    
    con = sqlite3.connect(dbBaseDatos)
    con.commit()
    con.close()

def crearTabla(dbBaseDatos):
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

def leerRegistros(dbBaseDatos):
    # Leer registros de la tabla productos
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM productos'):
        print(row)
    con.close()        

class create_dict(dict): 
    # __init__ function 
    def __init__(self): 
        self = dict() 
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value



@app.route('/productos', methods=['GET'])
def leerProductos():
    mydict = create_dict()
    con = sqlite3.connect(dbBaseDatos)
    cur = con.cursor()
    for row in cur.execute('SELECT * FROM productos'):
        mydict.add(row[0],({"descripcion":row[1],"cantidad":row[2],"precio":row[3]}))
        print(row)
    con.close() 
    lista_productos = json.dumps(mydict, indent=2, sort_keys=True)
    print(lista_productos)
    return lista_productos


if __name__ == "__main__":
       
    print(args)
    crearBD(dbBaseDatos)
    crearTabla(dbBaseDatos)
    leerRegistros(dbBaseDatos)
    app.run(debug=True, port=args.puerto)


   


