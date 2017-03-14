'''programa_facturacion escrito por Miguel Angel Gómez
28/2/17- publicado bajo licencia GPL
'''

class Boleta:
  def __init__(self,numbol=0,fecha='',cliente=0):
    self.cur=db.cursor()
    self.cur1=db.cursor()
    self.numbol=numbol
    self.fecha=fecha
    self.renglones=[]
    self.clie_id=cliente
    self.total=0     
    if self.numbol!=0:
      for n in self.cur.execute("select prod_id,cantidad from renglon where fact_id ={0}".format(self.numbol)):
        self.renglones.append(list(n))
      self.clie_id,self.fecha=self.cur.execute("select clie_id, fecha from facturas where id_fact={0}".format(self.numbol)).fetchone()
      print(self.fecha)
      self.total=int(self.cur.execute("select sum(precio_prod*cantidad)as total from productos,renglon where renglon.prod_id=productos.id_prod and renglon.fact_id={0}".format(self.numbol)).fetchone()[0])

  def setNumbol(self,numbol):
    self.numbol=numbol

  def setFecha(self,fecha):
    self.fecha=fecha

  def setClie(self,clie_id):
    self.clie_id=clie_id

  def addRenglon(self,id_prod,cant):
    self.renglones.append([id_prod,cant])

  def crearBoleta(self,fecha,cliente,auto=False):
    self.setNumbol(self.cur.execute("select max(id_fact)+1 from facturas ").fetchone()[0])
    self.setFecha(fecha)
    self.clie_id=cliente
    if auto:
      for est in self.cur.execute("select prod_id, cantidad from estadisticas where clie_id=?",(self.clie_id,)):
        prod_id,cantidades=est
        cant= int(random.choice(cantidades.split(',')))
        self.addRenglon(prod_id,cant)
    else:
      for est in self.cur.execute("select prod_id from estadisticas where clie_id=?",(self.clie_id,)):
        print(est)
        print(est[0])
        c=est[0]
        self.addRenglon(est[0],self.pideCantidad(est[0]))

  def pideCantidad(self,prod_id):
    print(prod_id)
    producto=self.cur1.execute("select desc_prod from productos where id_prod=?",(prod_id,)).fetchone()[0]
    cant=input("Ingrese la cantidad de {0}".format(producto))
    if cant.isdigit():
      return cant
    else:
      return pideCantidad(prod_id)   

  def mostrarBoleta(self):
    print("Nº:",self.numbol)  
    print("Fecha:",muestraFecha(self.fecha))
    cur=db.cursor()
    datos_clie=self.cur.execute("select nombre_clie,cuit_clie,localidad,desc_iva from clientes,localidades,tipo_iva where id_clie={0} and tipo_iva.id_iva=clientes.iva_id and localidades.id_loc=clientes.loc_id".format(self.clie_id)).fetchone()
    print("Cliente:",datos_clie[0])
    print("CUIT:",datos_clie[1])
    print("Localidad",datos_clie[2])
    print("IVA:",datos_clie[3])
    print("Cant\tProducto\t\tPrecio\tTotal")    
    for renglon in self.renglones :
      datos_prod=self.cur.execute("select desc_prod, precio_prod,precio_prod*{0} from productos where id_prod={1}".format(renglon[1],renglon[0])).fetchone()
      print(renglon[1],"\t",datos_prod[0],"\t\t",datos_prod[1],"\t",datos_prod[2])
      self.total+=datos_prod[2]
    print("Total: \t\t\t\t\t", self.total)

  def guardarBoleta(self):
    self.cur.execute("insert into facturas (fecha,clie_id) values('{0}',{1})".format(self.fecha,self.clie_id))
    for renglon in self.renglones:
      self.cur.execute("insert into renglon(fact_id,prod_id,cantidad)values({0},{1},{2})".format(self.numbol,renglon[0],renglon[1]))
    db.commit()


def pideNumClie():
  c=db.cursor()
  c.execute("select id_clie, nombre_clie from clientes;")
  for n in c:
    print(n)
  return int(input("Ingrese el numero de cliente"))

 # c.execute(" select cantidad,desc_prod,precio_prod from renglon,productos ,cantidad*precio_prod as total where fact_id=(select id_fact from facturas where facturas.clie_id=1)and productos.id_prod=renglon.prod_id;")  #sentencia para adquirir todos los renglones de un cliente

def crearTablas(db):
  try:
    print("Abriendo archivo...")
    f=open("creacion db","r")
  except FileNotFoundError:
    print("Archivo no encontrado")  
    return 1
  c=db.cursor()
  for n in f:      
    if  not n.startswith("/"):
      try:
          c.execute(n.strip())
      except sqlite3.OperationalError:
        print("Error en la base de datos")
      print(n)
    db.commit()
  return 1

def pideFecha():
  fecha=input("Ingrese fecha para facturacion(DD/MM/AAAA):")
  if compFecha(fecha):
    fecha=stdFecha(fecha)
    print(fecha)
    return fecha
  else:
    return pideFecha()

def compFecha(fecha):
  patron='(^[1-9]{1}|0[1-9]|[1-2][0-9]|3[0-1])[/-]([1-9]{1}|0[1-9]|1[0-2])[/-](201[0-9]$|1[0-9]$)'
  return re.match(patron,fecha) 
   
def muestraFecha(fecha):
  print(fecha)
  a,b,v=fecha.split("-")
  return v+'/'+b+'/'+a

def stdFecha(fecha): #sqlite3 usa el sig formato para almacenar strings de fechas:'yyyy-mm-dd'
  fecha=fecha.replace("-","/")
  d,m,y=fecha.split("/")
  if len(d)<2:
    d='0'+d
  if len(m)<2:
    m='0'+m
  if len(y)<4:
    y='20'+y
  return str(y+"-"+m+"-"+d)

def pideTipoFacturacion():
  opcion=input("Ingrese 'A' para facturar a todo los clientes o 'M' para facturar a uno:\n").upper()
  if opcion=='A':  
    return True
  elif opcion=='M':
    return False
  else:
    return pideTipoFacturacion()

def facturar():
  if pideTipoFacturacion():
    return facturarAuto()
  else:
    return facturarManual()

def facturarManual():
  nueva=Boleta()
  nueva.crearBoleta(fecha=pideFecha(),cliente=pideNumClie())
  sigue=False
  cont=0
  while(not sigue):
    nueva.mostrarBoleta()
    if input("Desea confirmar la boleta?").upper()=='S':
      sigue=True
    else:
      cont+=1
    if cont==3:
      return 1
    nueva.guardarBoleta()
    return 1
###seguir aca


def facturarAuto(db):
  fecha=pideFecha()
  c=db.cursor()
  c.execute("select * from clientes")
  c1=db.cursor()
  c2=db.cursor()
  for n in c:
    hecho='q'
    while hecho.upper() not in ['S','SI','Y','YES','']:  
      print("Factura Nº:\t",c1.execute("select max(id_fact )+1 from facturas;").fetchone()[0])
      print("Nombre:",n[1])
      print("CUIT:",n[2].replace(n[2][2:-1],"-{0}-".format(n[2][2:-1])))    
      c1.execute("select * from tipo_iva where id_iva={0};".format(n[4] ))
      print(c1.fetchone()[1])
      c1.execute("select * from localidades where id_loc={0};".format(n[3] ))
      print("localidad",c1.fetchone()[1])
      c1.execute("select prod_id,cant from estadisticas where clie_id={0};".format(n[0]))
      renglones=[]  
      total=0
      for i in c1:    #iteraciones para definir un renglon
        lista=[i[0]]  #estadisticas.prod_id 
        lista.append(int(random.choice(i[1].strip("'\n").split(","))))  #cantidad seleccionada aleatoria desde estadisticas.cant
        lista.append(c2.execute("select precio_prod from productos where  id_prod={}".format(i[0])).fetchone()[0]) #productos.precio
        lista.append(lista[1]*lista[2]) #subtotal del renglon
        total+=lista[3]
        renglones.append(lista)
      print("cantidad\tDescripcion\t\tPrecio unit.\tTotal")
      for i in renglones:
        if  i [1]>0:
          print(i[1],"\t\t",c2.execute("select desc_prod from productos where id_prod={0}".format(i[0])).fetchone()[0].ljust(22," "),"\t",i[2],"\t",i[3])
      print("\t\t\t\tTotal",total)
      hecho=input("Desea confirmar esta boleta?(Ingrese '0' para no facturar a este cliente)")
      if hecho=='0':  
        break
    if  hecho!='0':
      c1.execute("insert into facturas(fecha,clie_id)values('{0}',{1});".format(fecha , int(n[0])))
      for i in renglones:
        if i[1]>0:
          c1.execute("insert into renglon(fact_id,prod_id,cantidad)values((select max(id_fact) from facturas),{0},{1});".format(i[0],i[1]))
      db.commit()
      print("Cambios realizados")
  return 1

def actualizar_estadisticas(db):
  c=db.cursor()
  try:
    f=open("est-{0}".format(archivo.strip(".db")),"r")
  except FileNotFoundError:
    print("Archivo no encontrado")
    return 1
  c.execute("drop table estadisticas;")
  c.execute("create table estadisticas(clie_id integer not null,prod_id integer not null,cant text not null);")
  for n in f:
    print(n)
    c.execute("insert into estadisticas(clie_id,prod_id,cant)values(?,?,?)",n.split(";"))
  db.commit()
  return 1

def actualizar_clientes(db):
  c=db.cursor()
  f=open("./clientes-{0}".format(usuario.strip(".db")),"r")
  for n in f:
    clientes=n[:len(n)-1].split(";")
    print(clientes)
    c.execute('insert into clientes(nombre_clie,cuit_clie,loc_id,iva_id) values(?,?,?,?) ',clientes)
  f.close()
  db.commit()
  return 1

def pideLocalidad():
  loc=input("Ingrese el nombre de la localidad:\t")
  if input("La localidad {0} es correcta?".format(loc)) in ('s','S','y','Y'):
    return compLocalidad(loc)
  else:
    return pideLocalidad()

def compLocalidad(localidad):
  if localidad=='0':
    return 0
  elif len(localidad)<4:
    compLocalidad(input("Nombre de localidad demasiado corto.Reingrese('0'para salir):\t"))
  cur=db.cursor()
  for loc in cur.execute("select localidad from localidades"):
    if loc[0].upper()==localidad:
      print("Localidad existente")
      return 0
  return localidad

def agregarLocalidad():
  cur=db.cursor()  
  localidad=pideLocalidad()
  if localidad!=0:
    print(localidad)
    cur.execute("Insert into localidades (localidad)values(?)",(localidad,))
    db.commit()
    print("Se agrego {0} con el ID {1}".format(localidad,cur.execute("select max(id_loc)from localidades").fetchone()[0]))
  else:
    print("No se agrego una nueva Localidad")
  return 1     

def mostrarFact():
  opcion=input("Ingrese 'F' para ver las facturas por fecha\nIngrese 'C' para ver las facturas de un cliente")
  if opcion.upper()=='F':
    return mostrarFactFecha(pideFecha())
  elif opcion.upper()=='C':
    return mostrarFactClie(pideNumClie())
  else:
    return mostrarFact()

def mostrarFactFecha(fecha):
  c=db.cursor()
  for bol in c.execute("select id_fact from facturas where fecha=?",(fecha,)):
    actual=Boleta(bol[0])
    actual.mostrarBoleta()
    input('')
  return 1

def mostrarFactClie(clie_id):
  c=db.cursor()
  c.execute("select id_fact from facturas where clie_id={0};".format(clie_id))
  for bol in c:
   actual=Boleta(bol[0])
   actual.mostrarBoleta()  
   input("")
  return 1

def agregarDatos():
  opcion=input("Ingrese 'P' para agregar un Producto\nIngrese 'I' para agregar una descripcion de IVA\n")
  if opcion.upper()=='P':
    return agregarProducto()
  elif opcion.upper()=='I':
    return agregarIva()
  else:
    return agregarDato()

def agregarProducto():
  print("Ingrese '0' para cancelar")
  producto=input("Ingrese la descripcion del producto:\t")
  if producto=='0':
    return 1
  if input("Ingrese 's' si es correcto\n").upper()!='S'  :
    return agregarProducto()
  precio='a'
  while type(precio)!=float:
    precio=input("Ingrese el precio del producto:\t")
    try:  
      precio=round(float(precio),2)
    except ValueError:
      print("Ingrese un numero válido")
  if input("Ingrese 's' si es correcto\n").upper()!='S'  :
    return agregarProducto()
  c=db.cursor()
  c.execute("insert into productos (desc_prod,precio_prod)values(?,?)",(producto,precio))
  db.commit()
  return 1  

def agregarIva():
  print("Ingrese '0' para cancelar")
  tipo=input("Ingrese la situacion ante el IVA:\t")
  if tipo=='0':
    return 1
  if input("Ingrese 's' si es correcto\n").upper()!='S'  :
    return agregarIva()
  c=db.cursor()
  c.execute("insert into tipo_iva (desc_iva)values(?)",(tipo,))
  db.commit()
  return 1  
  
def menu(db):
  str_menu='''
  Ingrese 's' para agregar datos las tablas
  Ingrese 'al' para agregar una localidad
  Ingrese 'e' para  actualizar las estadisticas de compras
  Ingrese 'a' para actualizar la tabla de clientes con el archivo clientes
  Ingrese 'f' para realizar la facturacion mensual
  Ingrese 'm' para mostrar facturas
  Ingrese 'c' para crear las tablas
  Ingrese 'q' para salir 
'''
  men=input(str_menu)
  if men.upper() == "A" :
    return actualizar_clientes(db)
  elif men.upper()=='AL':
    return agregarLocalidad()
  elif men.upper() == 'F' :
    return facturar()
  elif men.upper()=='C':
    return crearTablas(db)
  elif men.upper()=='Q':
    return 0
  elif men.upper()=='E':
    return actualizar_estadisticas(db)
  elif men.upper()=='S':
    return agregarDatos()
  elif men.upper()=='M':
    return mostrarFact()#redefinir para mostrar las boletas de una fecha
  else:
    return menu(db)

import re
import random
import sqlite3
usuario=input("Ingrese nombre de la base de datos:")
db=sqlite3.connect(usuario+".db")
prog=1
while prog:
  prog=menu(db)
db.close()
