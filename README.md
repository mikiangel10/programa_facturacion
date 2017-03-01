# programa_facturacion
Programa en python3 para realizar facturas de un negocio, utiliza una base de datos sqlite3, con la tablas para clientes, con sus datos, productos e historial de facturas.

la version 1.0 subida el 28/2/17 se implementa sobre la linea de comandos, inicia con la pregunta por el nombre de la base de datos, el cual puede o existir en el directorio actual. (de no existir se crea). se debe ingresar solo el nombre de usuario que se escoja.
Cuenta con un menu inicial con las siguientes opciones:
c: crea las tablas de la base de datos- Necesario para un usuario nuevo. Obtiene los datos del archivo "creacion db".
a: actualiza la tabla "clientes", en base un archivo llamado "clientes-", seguido con el nombre del usuario, y con la siguiente estructura: "nombre y apellido cliente";cuit(8digitos);id_localidad;id_tipo de IVA
cada linea sera interpretada y agregada a la base de datos
f: para realizar la facturacion a todos los clientes de una fecha especifica. Utiliza una tabla que posee estadisticas de compra prefijadas de cada cliente sobre cada producto y selecciona aleatoriamente una de las cantidades enumeradas en la tabla "estadisticas"
e: actualiza la tabla "estadisticas" en base al archivo que se denomina "est-"nombredeusuario; con la siguiente estructura:
un numero con el id del cliente segun la tabla de clientes, separado por ';' otro numero con el id del producto, segun la tabla de productos, separado por otro ';' una cadena con las cantidades estadisticas que se anotaran, separadadas por ','. ej '1,1,2,3'
q: para salir del programa

