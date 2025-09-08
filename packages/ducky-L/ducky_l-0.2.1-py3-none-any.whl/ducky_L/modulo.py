import string, random
variables = {}

def poner(texto):
    if texto.startswith("*") and texto.endswith("*"):
        nombre_var = texto[1:-1]
        print(variables.get(nombre_var, f"$variable {nombre_var} no definida$"))
    else:
        print(texto)

def variable(nombre, valor):
    variables[nombre] = valor

def bucle(accion=None, condicion=None, n=None):
    if n is not None:
        for _ in range(n):
            accion()
    elif condicion is not None:
        while condicion():
            accion()
def si(condicion, hacer=None, condicion2=None, hacer2=None, sino=None):
    if condicion():
        hacer()
    elif condicion2():
        hacer2()
    else:
        sino()

def consola_nor(texto=None):
    input(f"$ {texto}")

def consola_var(texto=None, nombre_var=None):
    valor = input(f"$ {texto} ")
    if nombre_var:
        variables[nombre_var] = valor
    else:
        pass
    return valor

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


def LSL(html_file, static_dir="static", port=8000):
    app = FastAPI()

    # Monta la carpeta de archivos estáticos si existe
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Ruta principal
    @app.get("/")
    def home():
        # Usa os.path.abspath para obtener la ruta absoluta del archivo HTML
        # Esto asegura que el archivo se encuentre en la carpeta de ejecución
        html_path = os.path.abspath(html_file)
        return FileResponse(html_path)

    # Levanta el servidor
    uvicorn.run(app, host="0.0.0.0", port=port)

def password(length=10):
    elementos = string.ascii_letters + string.digits + string.ascii_uppercase + string.ascii_lowercase
    password = ""

    for _ in range(length):
        password += random.choice(elementos)
    return password

import datetime
def hora():
    hora = datetime.datetime.now()
    return hora

from pathlib import Path

def CC(carpeta):
    ruta = Path(carpeta)
    ruta.mkdir(parents=True, exist_ok=True)

def CA(archivo, contenido=""):
    try:
        with open(archivo, 'w') as archivo:
            archivo.write(contenido)
            print(f"El archivo '{archivo}' ha sido creado y escrito.")
    except Exception as e:
        print(f"Error al crear el archivo: {e}")


from cryptography.fernet import Fernet
def generar_clave():
    return Fernet.generate_key()

def encriptar(texto, clave):
    f = Fernet(clave)
    texto_bytes = texto.encode()
    return f.encrypt(texto_bytes)

def desencriptar(encriptado, clave):
    f = Fernet(clave)
    texto_desencriptado_bytes = f.decrypt(encriptado)
    return texto_desencriptado_bytes.decode()

import json
def escribir_json(nombre, datos):
    try:
        with open(nombre, 'w') as archivo:
            # json.dump() guarda los datos en el archivo
            json.dump(datos, archivo, indent=4)
        print(f"Datos guardados en '{nombre}' con éxito.")
    except Exception as e:
        print(f"Error al escribir en el archivo JSON: {e}")

def leer_json(nombre):
    try:
        with open(nombre, 'r') as archivo:
            # json.load() lee los datos del archivo
            datos = json.load(archivo)
            return datos
    except FileNotFoundError:
        print(f"Error: El archivo '{nombre}' no fue encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Error: El archivo '{nombre}' no tiene un formato JSON válido.")
        return None

import shutil
def copiar_archivo(origen, destino):
    try:
        shutil.copy(origen, destino)
        print(f"Archivo copiado de '{origen}' a '{destino}' con éxito.")
    except FileNotFoundError:
        print(f"Error: El archivo '{origen}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al copiar el archivo: {e}")

def eliminar_archivo(archivo):
    try:
        os.remove(archivo)
        print(f"Archivo '{archivo}' eliminado con éxito.")
    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error al eliminar el archivo: {e}")

def eliminar_carpeta(ruta_carpeta):
    try:
        # Verifica si la carpeta existe antes de intentar eliminarla
        if os.path.exists(ruta_carpeta):
            shutil.rmtree(ruta_carpeta)
            print(f"Carpeta '{ruta_carpeta}' y su contenido han sido eliminados.")
        else:
            print(f"Error: La carpeta '{ruta_carpeta}' no fue encontrada.")
    except Exception as e:
        print(f"Ocurrió un error al eliminar la carpeta: {e}")