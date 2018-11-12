#! /usr/bin/python3
'''programa_facturacion escrito por Miguel Angel Gómez
28/2/17- publicado bajo licencia GPL
'''

'''sentencias sql para obtener la suma mensual
sqlite> select sum (subtot) from select id_fact,fecha,nombre_clie,subtot from renglones where julianday(fecha)>julianday("2017-03-31");
Error: near "select": syntax error
sqlite> select id_fact,fecha,nombre_clie,subtot, sum (subtot) from renglones where julianday(fecha)>julianday("2017-03-31");
id_fact|fecha|nombre_clie|subtot|sum (subtot)
832|2017-04-28|"Maria Alejandra Tedesco"|296|11762
sqlite> 
Otra opcion:
sqlite> select sum (subtot) from renglones where strftime('%m',fecha)='04' ;

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
    self.erronea=False
    self.nula=False
    if self.numbol != 0:
      try:
        for n in self.cur.execute("select prod_id,cantidad,precio_id from renglones where id_fact ={0}".format(self.numbol)):
          self.renglones.append(list(n))
      except TypeError:
          self.erronea=True
          print("No hay renglones para esta factura Nº{0}".format(self.numbol))
      try:
        self.clie_id,self.fecha,self.nula=self.cur.execute("select clie_id, fecha, anulada from facturas where id_fact={0}".format(self.numbol)).fetchone()
      except TypeError:
        self.erronea=True
        print("No existe la factura Nº {0} en la base de datos".format(self.numbol))
      if len(self.renglones)>0:
        self.total=int(self.cur.execute("select sum(subtot) from renglones where id_fact={0}".format(self.numbol)).fetchone()[0])

  def setNula(self,anulada):
    self.nula=anulada
    self.cur.execute("update facturas set anulada={0} where id_fact={1}".format(anulada,self.numbol))
    db.commit()

  def setNumbol(self,numbol):
    self.numbol=numbol

  def setFecha(self,fecha):
    self.fecha=fecha

  def setClie(self,clie_id):
    self.clie_id=clie_id

  def addRenglon(self,id_prod,cant,id_precio):
    self.renglones.append([id_prod,cant,id_precio])

  def crearBoleta(self,fecha,cliente,auto=False):
    self.setNumbol(self.cur.execute("select max(id_fact)+1 from facturas ").fetchone()[0])
    self.setFecha(fecha)
    self.clie_id=cliente
    if auto:
      for est in self.cur.execute("select prod_id, cant,id_precio from estadisticas,precios where id_prod=prod_id and fecha_val=(select max(fecha_val) from precios) and clie_id=?",(self.clie_id,)):
        prod_id,cantidades,id_precio=est 
        cant= int(random.choice(cantidades.split(',')))
        self.addRenglon(prod_id,cant,id_precio)
    else:
      for est in self.cur.execute("select prod_id,id_precio from estadisticas,precios where id_prod=prod_id and fecha_val=(select max(fecha_val) from precios) and clie_id=?",(self.clie_id,)):
        #c=est[0]
        self.addRenglon(est[0],self.pideCantidad(est[0]),est[1])

  def pideCantidad(self,prod_id):
    print(prod_id)
    producto=self.cur1.execute("select desc_prod from productos where id_prod=?",(prod_id,)).fetchone()[0]
    cant=input("Ingrese la cantidad de {0}".format(producto))
    if cant.isdigit():
      return int(cant)
    else:
      return pideCantidad(prod_id)   

  def mostrarBoleta(self):
    if self.erronea:
      print("Boleta Nº{0} con errores en la base de datos".format(self.numbol))
      return 0
    print('**'*30)
    print("Nº:",self.numbol)  
    print("Fecha:",muestraFecha(self.fecha))
    cur=db.cursor()
    datos_clie=self.cur.execute("select nombre_clie,cuit_clie,localidad,desc_iva from clientes,localidades,tipo_iva where id_clie={0} and tipo_iva.id_iva=clientes.iva_id and localidades.id_loc=clientes.loc_id".format(self.clie_id)).fetchone()
    print("Cliente:",datos_clie[0])
    print("CUIT:",datos_clie[1])
    print("Localidad",datos_clie[2])
    print("IVA:",datos_clie[3])
    print("Cant\tProducto\t\tPrecio\tTotal")    
    self.total=0
    for renglon in self.renglones :
      datos_prod=self.cur.execute("select desc_prod,valor from productos,precios where productos.id_prod={0} and precios.precio_id={1}".format(renglon[0],renglon[2])).fetchone()
      print(renglon)
      print(datos_prod)
      subt=datos_prod[1]*renglon[1]
      print(renglon[1],"\t",datos_prod[0],"\t\t",renglon[2],"\t",subt)
      self.total+=subt
    print("Total: \t\t\t\t\t", self.total)

  def guardarBoleta(self):
    if self.cur.execute("select * from facturas where id_fact={0}".format(self.numbol)).fetchone() != None:
      self.cur.execute("update facturas set fecha={0},clie_id={1}, anulada={2} where id_fact={3}".format(self.fecha,self.clie_id,self.nula,self.numbol))
    else:
#      self.cur.execute("insert into facturas (id_fact,fecha,clie_id,anulada) values({0},'{1}',{2},{3})".format(self.numbol,self.fecha,self.clie_id,self.nula))
      self.cur.execute("insert into facturas (id_fact,fecha,clie_id) values({0},'{1}',{2})".format(self.numbol,self.fecha,self.clie_id))
      for renglon in self.renglones:
        self.cur.execute("insert into renglon(fact_id,prod_id,cantidad,id_precio)values({0},{1},{2})".format(self.numbol,renglon[0],renglon[1],renglon[2]))
    db.commit()

  def imprimir(self):
    import os
    from reportlab.pdfgen import canvas
    datos_clie=self.cur.execute("select nombre_clie,cuit_clie,dom_clie,localidad,desc_iva from clientes,localidades,tipo_iva where id_clie={0} and tipo_iva.id_iva=clientes.iva_id and localidades.id_loc=clientes.loc_id".format(self.clie_id)).fetchone()
    nombre=str(datos_clie[0])
    cuit=str(datos_clie[1])
    cuit=cuit[:2]+'-'+cuit[2:-1]+'-'+cuit[-1:]    
    domicilio=datos_clie[2]
    localidad=datos_clie[3]
    iva_clie=datos_clie[4]
    aux=canvas.Canvas("boleta.pdf",pagesize=(478,600))
    cx_dia=363
    cx_mes=398
    cx_ano=436
    cy_fecha=477
    cx_nombre=55*2.83
    cy_nombre=146*2.83
    cx_domicilio=53*2.83
    cx_localidad=132*2.83
    cy_domicilio=139.5*2.83
    cx_cuit=115*2.83
    cy_cuit=133*2.83
    cx_iva={"Monotributo":66*2.83,"exento":83*2.83,"Responsable Inscripto":62.5*2.83,"final":83*2.83 }
    cy_iva={"Monotributo":134*2.83,"exento":134*2.83,"Responsable Inscripto":131.5*2.83,"final":131.5*2.83}
    cx_contado=61.5*2.83
    cy_contado=124.5*2.83
    cx_cant=40*2.83
    cx_prod=52*2.83
    cx_precio=132*2.83
    cx_importe=155*2.83
    cy_renglon=114*2.83
    salto_renglon=5.5*2.83
    cx_total=152*2.83
    cy_total=38*2.83

    aux.setFontSize(12)
    aux.drawString(cx_dia,cy_fecha,self.fecha.split('-')[2]) #imprime el dia
    aux.drawString(cx_mes,cy_fecha,self.fecha.split('-')[1]) #imprime el mes
    aux.drawString(cx_ano,cy_fecha,self.fecha.split('-')[0][2:])#imprime los dos digitos del año
    aux.drawString(cx_nombre,cy_nombre,nombre[1:-1])#imprime el nombre del cliente
    aux.setFontSize(10)
    aux.drawString(cx_domicilio,cy_domicilio,domicilio)#imprime el domicilio
    aux.drawString(cx_localidad,cy_domicilio,localidad)
    aux.drawString(cx_cuit,cy_cuit,cuit)
    aux.drawString(cx_iva[iva_clie],cy_iva[iva_clie],"x")#pone la x en la casilla correspondiente
    aux.drawString(cx_contado,cy_contado,"x")#pone x en condicion de contado
    cont=0 
    for renglon in self.renglones:
      producto=self.cur.execute("select desc_prod from productos where id_prod={0}".format(renglon[0])).fetchone()
      precio=self.cur.execute("select valor from precios where id_precio={0}".format(renglon[2])).fetchone()
      aux.drawString(cx_cant,cy_renglon-salto_renglon*cont,str(renglon[1]))
      aux.drawString(cx_prod,cy_renglon-salto_renglon*cont,producto)
      aux.drawString(cx_precio,cy_renglon-salto_renglon*cont,'{:.2f}'.format(precio))
      aux.drawString(cx_importe,cy_renglon-salto_renglon*cont,'{:.2f}'.format(precio*renglon[1]))
      print (cont)
      cont+=1;
    aux.setFontSize(14)
    aux.drawString(cx_total,cy_total,'{:.2f}'.format(self.total))
    aux.showPage()
    aux.save()
    os.system("lpr -#2 boleta.pdf")

def anularBoletas():
  sigue=True
  while sigue :
    opcion=input("Ingrese el numero de Boleta que desea anular('0' para cancelar)\n")
    if opcion.isdigit():
      if int(opcion)==0:
        sigue=False
        print("break")
        break
      bol=Boleta(int(opcion))
      bol.mostrarBoleta()
      if not bol.erronea:
        sigue=False
        if bol.nula : #si la boleta ya fue anulada, preguntamos para revertir al condicion
          bol.mostrarBoleta()
          opcion=input("La boleta esta anulada. Desea revertir?(s/N)")
          if opcion.upper() == 'S':
            bol.setNula(0) #y seteamos la Nulidad a 0 
            db.commit()
            #bol.guardarBoleta()  fijarse porque no guarda correctamente las fechas el problema esta en el metodo guardarBoleta
            print("Boleta dada de alta")
          else:
            print("Cancelado")
        else:	#si la boleta no es nula
          bol.mostrarBoleta()
          opcion=input("Desea anular esta boleta?(S/n)")
          if opcion.upper() != 'N':
            bol.setNula(1)
            db.commit()
            #bol.guardarBoleta()
            print("Boleta anulada")
          else:
            print("Cancelado")
      else:
        print("La boleta presenta anormalidades en la base de datos")
    else:
      print("Ingresó un numero no valido")
  return 1
			
def sumaMensual(fecha):
  if fecha=='':
    fecha=datetime.datetime.strftime(datetime.datetime.today(),'%m/%y')
  if len(fecha.split('/')) != 2:
    print("Ingrese 'mm/aa' ")
    return 1
  else:
    mes,ano=fecha.split('/')
    mes=int(mes)
    ano=int(ano)
    if 0>mes>12 :
      print("Ingrese un mes entre 1 y 12")
      return 1
    if ano <99:
      ano+=2000  
  c=db.cursor()
  sfecha=stringFecha(mes,ano)
  c.execute("select sum (subtot) from renglones where strftime('%m/%Y',fecha)='{0}'".format(sfecha))
  sumaMes=c.fetchone()[0]
  if sumaMes == None:
    if mes == 1:
      mes=12
      ano=ano-1
    else :
      mes=mes-1
    fecha=str(mes) + '/' + str(ano)
    print("Calculando el mes anterior ",(fecha))
    return sumaMensual(fecha)
  print("La suma mensual es $"+str(sumaMes))
  sumaAnio=int(sumaMes)
  for n in range(11):
    if mes==1:
      mes=12
      ano-=1
    else:
      mes-=1
    sfecha=stringFecha(mes,ano)
    c.execute("select sum (subtot) from renglones where strftime('%m/%Y',fecha)='{0}'".format(sfecha))
    sumaMes=c.fetchone()[0]
    if sumaMes==None:
      print("Faltan "+str(11-n)+" meses de datos. ")
      break;
    sumaAnio+=int(sumaMes)
  print("La suma del útlimo año es $"+str(sumaAnio))
  return 1

def stringFecha(mes,ano):
  if mes<10: 
    smes="0"+str(mes)
  else:
    smes=str(mes)
  return smes+'/'+str(ano)

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
    return fecha
  else:
    return pideFecha()

def compFecha(fecha):
  patron='(^[1-9]{1}|0[1-9]|[1-2][0-9]|3[0-1])[/-]([1-9]{1}|0[1-9]|1[0-2])[/-](201[0-9]$|1[0-9]$)'
  return re.match(patron,fecha) 
   
def muestraFecha(fecha):
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

def facturarManual(fecha=0,cliente=0):
  nueva=Boleta()
  if fecha == 0 :
    fecha=pideFecha()
  if cliente==0:
    cliente=pideNumClie()
  nueva.crearBoleta(fecha,cliente)
  sigue=False
  cont=0
  while(not sigue):
    nueva.mostrarBoleta()
    if input("Desea confirmar la boleta?(S/n)").upper() != 'N':
      sigue=True
    else:
      cont+=1
    if cont==3:
      return 1
  nueva.guardarBoleta()
  imprimir=input("Cambios realizados.¿Desea Imprimir?(S/n)")
  if imprimir.upper() != 'N':
    nueva.imprimir()
    print("Impresa...")
  return 1


def hacerBackup():
  comentario="Backup a las: "+str(datetime.datetime.today())
  repo=git.Repo("./")
  repo.git.add(".")
  try:
    repo.git.commit(m=comentario)
    print(comentario)
  except :
    print("Sin modificaciones desde el último Backup")
  repo.close()

def facturarAuto():
  fecha=pideFecha()
  c=db.cursor()
  c.execute("select * from clientes where stat_clie=1;")
  c1=db.cursor()
  c2=db.cursor()
  for n in c:
    hecho='q'
    while hecho.upper() not in ['S','SI','Y','YES','']:  
      print("Fecha: "+fecha)
      numero_boleta=c1.execute("select max(id_fact )+1 from facturas;").fetchone()[0]
      print("Factura Nº:\t",numero_boleta)
      print("Nombre:",n[1])
      print("CUIT:",n[2].replace(n[2][2:-1],"-{0}-".format(n[2][2:-1])))    
      c1.execute("select * from tipo_iva where id_iva={0};".format(n[4] ))
      print(c1.fetchone()[1])
      c1.execute("select * from localidades where id_loc={0};".format(n[3] ))
      print("localidad",c1.fetchone()[1])
      c1.execute("select prod_id,cant from estadisticas where clie_id={0};".format(n[0]))#cantidad
      renglones=[]  
      total=0
      for i in c1:    #iteraciones para definir un renglon
        lista=[i[0]]  #estadisticas.prod_id 
        lista.append(int(random.choice(i[1].strip("'\n").split(","))))  #cantidad seleccionada aleatoria desde estadisticas.cant
        id_pre,val=c2.execute("select precio_id,valor from precios where fecha_val=(select max(fecha_val) from  precios where fecha_val <= {0} ) and id_prod={1}".format(fecha,i[0])).fetchone() #precios.id_precio precios.valor
        lista.append(val)
        lista.append(lista[1]*lista[2]) #subtotal del renglon
        total+=lista[3]
        lista.append(id_pre)
        renglones.append(lista)
      print("cantidad\tDescripcion\t\tPrecio unit.\tTotal")
      for i in renglones:
        if  i [1]>0:
          print(i[1],"\t\t",c2.execute("select desc_prod from productos where id_prod={0}".format(i[0])).fetchone()[0].ljust(22," "),"\t",i[2],"\t",i[3])
      print("\t\t\t\tTotal",total)
      if total==0:
        hecho=input("Factura vacia para este cliente...Presione enter para rehacer('0' para seguir)\n")
      else:  
        hecho=input("Desea confirmar esta boleta?(Ingrese '0' para no facturar a este cliente,o 'M' para modificar manualmente)\n")
      if hecho=='0':  
        break
      if hecho.upper()=='M':
        facturarManual(fecha,n[0])
        hecho='0'
        break
    if  hecho!='0':
      c1.execute("insert into facturas(id_fact,fecha,clie_id)values({0},'{1}',{2});".format(numero_boleta,fecha , int(n[0])))
      for i in renglones:
        if i[1]>0:
          c1.execute("insert into renglon(fact_id,prod_id,cantidad,id_precio)values((select max(id_fact) from facturas),{0},{1},{2});".format(i[0],i[1]),i[4])
      db.commit()
      imprimir=input("Cambios realizados.¿Desea Imprimir?(S/n)")
      if imprimir.upper() != 'N':
        factura=Boleta(numero_boleta)
        factura.imprimir()
        print("Impresa...")
      
  return 1

def actualizar_estadisticas(db):
  c=db.cursor()
  try:
    f=open("est-{0}".format(usuario.strip(".db")),"r")
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

menu_muestra_fact='''
Ingrese 'F' para ver las facturas por fecha
Ingrese 'C' para ver las facturas de un cliente
Ingrese 'U' para ver las ultimas facturas
'''
def mostrarFact():
  opcion=input(menu_muestra_fact).upper()
  if opcion=='F':
    return mostrarFactFecha(pideFecha())
  elif opcion=='C':
    return mostrarFactClie(pideNumClie())
  elif opcion=='U':
    return mostrarUltimas()
  else:
    return mostrarFact()

def mostrarFactFecha(fecha):
  c=db.cursor()
  paso=0
  for bol in c.execute("select id_fact from facturas where fecha=?",(fecha,)):
    paso=1
    actual=Boleta(bol[0])
    actual.mostrarBoleta()
  if not paso:
    print('No hay facturas para la fecha indicada')
    input=('')
  return 1

def mostrarFactClie(clie_id):
  c=db.cursor()
  paso=0
  c.execute("select id_fact from facturas where clie_id={0};".format(clie_id))
  for bol in c:
    paso=1
    actual=Boleta(bol[0])
    actual.mostrarBoleta()  
  if not paso:
    print("No hay facturas emitidas a este cliente")
    input=('')
  return 1

def mostrarUltimas(ult=0):
  if ult==0:
    cur=db.cursor()  
    ult=cur.execute("select max(id_fact) from facturas").fetchone()[0]
  for n in range(3):
    if ult>0:
      actual=Boleta(ult)
      actual.mostrarBoleta()
      ult-=1
  opcion=input("Ingrese 'm' para ver mas o 's' para salir").upper()
  while opcion not in ('M','S'):
    opcion=input("Ingrese 'm' para ver mas o 's' para salir").upper()
  if opcion=='M':
    return mostrarUltimas(ult)
  elif opcion=='S':
    return 1

menu_agreg_datos='''
Ingrese 'P' para agregar un Producto
Ingrese 'I' para agregar una descripcion de IVA
Ingrese 'L' para agregar una localidad
Ingrese 'C' para agregar un cliente
   '''
def agregarDatos():
  opcion=input(menu_agreg_datos).upper()
  if opcion.upper() == 'P' :
    return agregarProducto()
  elif opcion.upper() == 'L' :
    return agregarLocalidad()
  elif opcion.upper() == 'I' :
    return agregarIva()
  elif opcion.upper() == 'C' :
    return agregarCliente()
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
  c.execute("insert into productos (desc_prod)values(?)",(producto))
  c.execute("insert into precios (valor,fecha_val)values(?,?)",(precio,str(datetime.date.today())))
  db.commit()
  print("Se agrego {0},precio {2} con el ID {1}".format(producto,cur.execute("select max(id_prod)from productos").fetchone()[0]),precio)
  return 1  

def agregarCliente() :
  nombre=input("Ingrese nombre del cliente\n")
  cuit=int(input("Ingrese el cuit del cliente.(sin guiones)\n"))
  direccion=input ("Ingrese domicilio\n")
  c=db.cursor()
  localidades=c.execute("select * from localidades;")
  ids=[]
  sigue=False
  while sigue != 's':
    for loc in localidades:
      print(loc)
      ids.append(loc[0])
    locId=input("Seleccione una localidad.Inserte solo el Id.\n") 
    if locId.isdigit() :
      if int(locId) in ids :
        sigue='s'
  ivas=c.execute("select * from tipo_iva;")
  ids=[]
  sigue=False
  while sigue != 's':
    for item in ivas :
      print(item)
      ids.append(item[0])
    ivaId=input("Seleccione un tipo de situacion ante AFIP")
    if ivaId.isdigit() :
      if int(ivaId) in ids :
        sigue='s'
  localidad=c.execute("select * from localidades where id_loc=?",(locId)).fetchone()
  iva=c.execute("select * from tipo_iva where id_iva=?",(ivaId)).fetchone()
  opcion=input("Desea agregar al cliente {0}, cuit {1}\n domicilio {2} de {3} Iva: {4} (S/n)".format(nombre,cuit,direccion,localidad[1],iva[1]))
  if opcion.upper() != 'N':
    c.execute("insert into clientes(nombre_clie,cuit_clie,loc_id,iva_id,dom_clie,stat_clie) values(?,?,?,?,?,1)",(nombre,cuit,int(localidad[0]),int(iva[0]),direccion))
    db.commit()
    return 1
  else :
    return 1

def imprimir_auto(numbol):
   imprime(numbol)
   opcion=input("Ingrese 'S' para seguir\nIngrese 'R' para reimprimir\nIngrese 'Q' para parar").upper()
   if opcion=='S':
    return imprimir_auto(int(numbol)+1)
   elif opcion=='R':
    return imprimir_auto(numbol)
   elif opcion=='Q':
    return 1 
   else:
    print("Opcion incorrecta. Abortando. \n Ultima factura impresa Nº",numbol)
    return 1
        
def imprime(numbol):
    try:
      factura=Boleta(numbol)
    except:
      print("No se encuentra la factura Nº:",numbol)
      return 1
    factura.mostrarBoleta()
    if input("¿Desea imprimir esta factura?(S/n)").upper()!='N':
      factura.imprimir()
      print("Impresa...")
      return 1
    else:
      print("Descartando impresion...")
      return 1
  
def imprimir():
  opcion=input("Ingrese 'M' para imprimir una boleta \n Ingrese 'A' para imprimir una secuencia").upper()
  if opcion=='M':
    numbol=input("Ingrese el numero de factura a imprimir:")
    return imprime(numbol)
  elif opcion=='A':
    numbol=input("Ingrese el numero de factura para iniciar:")
    return imprimir_auto(numbol)
  else:
    print("Opcion incorrecta")
    return imprimir() 

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
  print("Se agrego {0} con el ID {1}".format(tipo,cur.execute("select max(id_iva)from tipo_iva").fetchone()[0]))
  return 1  
  
def menu(db):
  str_menu='''
  Ingrese 's' para agregar datos a las tablas
  Ingrese 'e' para  actualizar las estadisticas de compras
  Ingrese 'a' para actualizar la tabla de clientes con el archivo clientes
  Ingrese 'f' para realizar una facturacion 
  Ingrese 'm' para mostrar facturas
  Ingrese 'c' para crear las tablas
  Ingrese 'x' para ver la suma mensual
  Ingrese 'i' para imprimir boletas
  Ingrese 'n' para anular boletas
  Ingrese 'q' para salir 
'''
  men=input(str_menu)
  if men.upper() == "A" :
    return actualizar_clientes(db)
  elif men.upper() == 'F' :
    return facturar()
  elif men.upper() == 'I' :
    return imprimir()
  elif men.upper()=='C':
    return crearTablas(db)
  elif men.upper()=='Q':
    return 0
  elif men.upper()=='E':
    return actualizar_estadisticas(db)
  elif men.upper()=='S':
    return agregarDatos()
  elif men.upper()=='N':
    return anularBoletas()
  elif men.upper()=='X':
    return sumaMensual(input("Ingrese el mes a sumar('mm/aa')"))
  elif men.upper()=='M':
    return mostrarFact()#redefinir para mostrar las boletas de una fecha
  else:
    return menu(db)

import datetime
import git
import re
import random
import sqlite3
hacerBackup()
usuario=input("Ingrese nombre de la base de datos:")
db=sqlite3.connect(usuario+".db")
while menu(db):
  pass
db.close()
