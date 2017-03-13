'''programa_facturacion escrito por Miguel Angel Gómez
28/2/17- publicado bajo licencia GPL
'''

class Boleta:
  def __init__(self,numbol=0):
    self.cur=db.cursor()
    self.numbol=numbol
    self.renglones=[]
    if numbol==0:
      self.clie_id='0'
      self.fecha=time.strftime('%Y-%m-%d')
      self.total=0     
    else:
      for n in self.cur.execute("select prod_id,cantidad from renglon where fact_id ={0}".format(self.numbol))
        renglones.append(list(n))
      self.clie_id,self.fecha=self.cur.execute("select clie_id, fecha from facturas where id_fact={0}".format(self.numbol)).fetchone()
      self.total=int(self.cur.execute("select sum(precio_prod*cantidad)as total from productos,renglon where renglon.prod_id=productos.id_prod and renglon.fact_id={0}".format(self.numbol)).fetchone()[0])
  def setNumbol(numbol):
    self.__init__(numbol)
  def setFecha(fecha=''):
    if fecha=='':    
      self.fecha= pedirFecha() 
    elif compFecha(muestraFecha(fecha)):
      self.fecha=muestraFecha(fecha)      
  def addClie(clie_id):
    self.clie_id=str(clie_id)
  def addRenglon(self,id_prod,cant):
    renglones.append([id_prod,cant])
  def mostrarBoleta(self):
    print("Nº:",self.numbol)  
    print("Fecha:",muestraFecha(self.fecha))
    cur=db.cursor()
    datos_clie=self.cur.execute("select nombre_clie,cuit_clie,localidad,desc_iva from clientes,localidades,tipo_iva where id_clie={0} and tipo_iva.id_iva=clientes.iva_id and localidades.id_loc=clientes.loc_id".format(self.clie_id)).fetchone()
    print("Cliente:",datos_clie[0])
    print("CUIT:",datos_clie[1])
    print("Localidad",datos_clie[2])
    print("IVA:"datos_clie[3])
    print("Cant\tProducto\t\tPrecio\tTotal"    
    for renglon in self.renglones:
      datos_prod=self.cur.execute("select desc_prod, precio_prod,precio_prod*{0} from productos where id_prod={1}".format(renglon[1],rengon[0])).fetchone()
      print(renglon[1],"\t",datos_prod[0],"\t\t",datos_prod[1]"\t",datos_prod[2])
      self.total+=datos_prod[2]
    print("Total: \t\t\t\t\t", total)
  def guardarBoleta(self):
    self.cur.execute("insert into facturas (fecha,clie_id) values({0},{1}".format(self.fecha,self.clie_id))
    for renglon in self.renglones:
      self.cur.execute("insert into renglon(fact_id,prod_id,cantidad)values({0},{1},{2})".format(self.numbol,renglon)
    db.commit()

def pideNumClie():
  c=db.cursor()
  c.execute("select id_clie, nombre_clie from clientes;")
  for n in c:
    print(n)
  return int(input("Ingrese el numero de cliente"))

def mostrarFactClie(clie_id):
  c=db.cursor()
  c1=db.cursor()
  c.execute("select id_fact from facturas where clie_id={0};".format(clie_id))
  for n in c:
   actual=Boleta(n[0])
   actual.mostrarBoleta()  
 # c.execute(" select cantidad,desc_prod,precio_prod from renglon,productos ,cantidad*precio_prod as total where fact_id=(select id_fact from facturas where facturas.clie_id=1)and productos.id_prod=renglon.prod_id;")  #sentencia para adquirir todos los renglones de un cliente

  input("")
  return 1


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

def pedirFecha():
  fecha=input("Ingrese fecha para facturacion(DD/MM/AAAA):")
  if compFecha(fecha):
    return std_fecha(fecha)
  else:
    return pedirFecha()

def compFecha(fecha):
  patron='(^[1-9]{1}|0[1-9]|[1-2][0-9]|3[0-1])[/-]([1-9]{1}|0[1-9]|1[0-2])[/-](201[0-9]$|1[0-9]$)'
  return re.match(patron,fecha) 
   
def muestraFecha(str):
  a,b,v=fecha.split("/")
  return v+'/'+b+'/'+a

def std_fecha(fecha): #sqlite3 usa el sig formato para almacenar strings de fechas:'yyyy-mm-dd'
  fecha=fecha.replace("-","/")
  d,m,y=fecha.split("/")
  if len(d)<2:
    a='0'+a
  if len(m)<2:
    b='0'+b
  if len(y)<4:
    y='20'+y
  return str(y+"-"+m+"-"+d)

def facturacion_manual():
  cur=db.cursor()
  desc_prod=cur.execute("select desc_prod from estadisticas,productos where productos.id_prod=estadisticas.prod_id and estadisticas.clie_id=?;" pideNumClie())
  for n in desc_prod:
    a=input("Ingrese la cantidad de",n[0],"a facturar:")
    
###seguir aca


def facturarAuto(db):
  fecha=pedirFecha()
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

def menu(db):
  str_menu='''Ingrese 'e' para  actualizar las estadisticas de compras
  Ingrese 'a' para actualizar la tabla de clientes con el archivo clientes
  Ingrese 'f' para realizar la facturacion mensual
  Ingrese 'm' para mostrar facturas segun fecha
  Ingrese 'fm' para realizar una factura manualmente
  Ingrese 'b' para mostrar las boletas de un cliente
  Ingrese 'c' para crear las tablas
  Ingrese 'q' para salir  '''
  men=input(str_menu)
  if men.upper() == "A" :
    return actualizar_clientes(db)
  elif men.upper() == 'F' :
    return facturarAuto(db)
  elif men.upper()=='C':
    return crearTablas(db)
  elif men.upper()=='Q':
    return 0
  elif men.upper()=='E':
    return actualizar_estadisticas(db)
  elif men.upper()=='M':
    return mostrarFactClie(pideNumClie())#redefinir para mostrar las boletas de una fecha
  elif men.upper()=='B':
    return boletas_clie()#definir boletas_clie-para mostrar las boletas de un determinado cliente
  elif men.upper()=='FM':
    return factura_man()#definir la funcion para hacer una factura manualmente
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
