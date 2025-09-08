duckyL es una libreria/lenguaje que sirve para codigo en español
´´´
pytho en español:

poner("text") <-- entre comillas el texto

variable("pato", "algo") <-- el primer parametro es el nmbre de la variable y el segundo el valor de la variable

poner("*pato*") <-- entre * se pondra cuando se llama una variable

variables["pato"] <--- es llamar una variable

si(variables["pato"] == "algo", lambda: poner("pato"), None, None) <-- el si() tiene 4 parametros: el if elif y else (solo 1 para cada uno) se usan los lambdas: algo, para poner que  se hara, el pimer parametro sera para la condicion, segundo para if, tercero elif y cuarto else

bucle(2, lambda: poner("pao")) <-- habran 3 parametros: accion, conndicion, cantidad, la acciones lo que se va a hacer, la condicion es porque se ejecuta (si no hay se puede poner None) y cantidad que sera las veses que se repita

consola_nor("texto: ") <-- sera para poner texto en la consola como un input

consola_var("texto: ", "2") <-- sera para poder crear una variable que se llame como se ponga en el segundo parametro y su valor sera el que se ponga en la consola 

utilidades:

LSL(index.html, "static", port=8000) <-- esto es para poder levantar un servidor local, en el primer argumento se pone el index.html (en la misma carpeta) en el segundo se pone la carpeta donde estan los archivos css y js (recomendado nombre "static") y el ultiumo se pone el puerto 

hora() <-- da la hora

crear_qr(url, nombre) <-- sirve para crear un qr con la url que le pongas

anima("texto", delay) <-- sirve para poder animar el texto que pongas en el primer parameto y el delay es el tiempo entre cada letra

print(color("texto", verde)) <-- sirve para ponerle color al texto, puedes poner: negro, rojo, verde, azul, amarillo, magenta, cyan, blanco, blanco_brillante, cyan_claro, magenta_claro, azul_claro, amarillo_claro, verde_claro, rojo_claro, gris_claro

encriptacion:
generar_clave(): <-- devulve una clave unica para poder hacer la encriptacion (nececita almacenar en una variable)

encriptar(texto, clave) <-- en el primer parametro se pone el texto a encriptar en el segundo se pone la clave generada 

desencriptar(encriptado, clave) <-- en el primer parametro se pone el texto encriptado (sin comillas) y en el segundo la clave (si no se tiene la cave o se peude desencriptar)

ejemplo de uso:
from ducky_L import *
clave = generar_clave()
texto = "hola mundo"

encriptado = encriptar(texto, clave)
print(encriptado)
print(desencriptar(encriptado, clave))

Json:
escribir_json(nombre, datos) <-- se usa para poder escribir json de una forma facil y rapida

#ejemplo de uso
datos_para_guardar = {
    "nombre": "Juan",
    "edad": 30,
    "ciudad": "Madrid",
    "habilidades": ["Python", "FastAPI", "Web Dev"]
}

escribir_json("perfil.json", datos_para_guardar)
===
leer_json(nombre_del_archivo) <-- sirve para leer un json

Del sistema:

copiar_archivo(archivo, destino) <-- sirve para duplicar archivos, en el primer parametro se pone el archivo (debe estar en la misma carpeta o sub carpeta, si no  se tiene que poner la ruta exacta) y el destino es donde se pondra el archivo dupicado

eliminar_archivo(archivo) <-- sirve para eliminar un archivo y en el unico parametro hay que poner la ruta del archivo

eliminar_carpeta(carpeta) <-- sirve para eliminar una carpeta y en el unico parametro hay que poner la ruta del archivo

CC("algo") <-- esto crea una carpeta con el nombre que le pongas

CA(nombre, contenido) <-- esto crea un archivo en la misma carpeta donde se ejecute el codigo con el nombre que se coloque y puedes poner de una vez texto e contenido (puedes no poner nada en contenido)

´´´
A todos los parametros que no se usan se puede poner None