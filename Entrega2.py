import serial
import utm
import threading
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pygame

serialPort = serial.Serial(port = "COM3", baudrate=4800,
                           bytesize=serial.EIGHTBITS, timeout=1, stopbits=serial.STOPBITS_ONE)
lock=threading.Lock() 
mensajeOriginal = bytearray(200)
cabecera = bytearray(6)
posicion = tuple()
punto0X = 425195.21    # miCasa
punto0Y = 4483420.69
#punto0X = 445941.81
#punto0Y = 4471507.52    #uni


def latAgrados(mensajeOriginal):
  s = mensajeOriginal.split(",")
  lat = float(s[2])
  dirLat = s[3]
  grad = int(lat / 100)
  min = float(lat - (grad * 100))
  grados = float(grad + (min / 60.0))
  if dirLat == "S":
    grados = -(grados)
  return grados, dirLat

def lonAgrados(mensajeOriginal):
 s = mensajeOriginal.split(",")
 long = float(s[4])
 dirLon = s[5]
 grad = int(long / 100)
 min = float(long - (grad * 100))
 grados = float(grad + (min / 60.0))
 if dirLon == "W":
   grados = -(grados)
 return grados, dirLon

def listener(lock):
  aux = ''
  serialPort.reset_input_buffer()
  serialPort.reset_output_buffer()    
  sig_msg = False
  mensajeCompleto = False
  while serialPort.isOpen() and mensajeCompleto==False:     
    global mensajeOriginal
    aux = serialPort.read()
    if aux == str.encode("$") or sig_msg: 
      sig_msg = False
      cabecera = serialPort.read(5)
      if cabecera == str.encode("GPGGA"):
        mensajeOriginal = ''
        aux = serialPort.read()
        while aux != str.encode("$"):
          mensajeOriginal = mensajeOriginal + bytes.decode(aux)
          aux = serialPort.read()
        sig_msg=True
        mensajeCompleto=True;
  serialPort.reset_input_buffer()
  serialPort.reset_output_buffer()

    
def caster(mensajeOriginal,lock):
  latitudEnGrados, dirLat = latAgrados(mensajeOriginal)
  longitudEnGrados, dirLon = lonAgrados(mensajeOriginal)
  print ("Latitud", latitudEnGrados, "(",dirLat,")")
  print ("Longitud",longitudEnGrados,"(",dirLon,")")
  global posicion
  posicion = utm.from_latlon(latitudEnGrados, longitudEnGrados)
  print (posicion)

def mostrarPunto(posicion, lock):

#---------con pyGame----------------------------------------------------------------------------#
  pygame.init()
  pantalla = pygame.display.set_mode([1920,1080], pygame.SCALED)  #display de la pantalla (valores adecuados a mi monitor 1530,800) muy raro  ¿SE PUEDE REESCALAR LA IMAGEN SEGÚN EL DISPOSITIVO EN EL Q ESTE?
  clock = pygame.time.Clock()  # Controlar FPS  (cuanto de rapido quiero que se mueva mi personita)
  cerrarGPS = False #variable para salir del bucle infinito
  imagen = pygame.image.load("miCasa.jpg").convert_alpha() #cargar la img de fondo (etsisi+insia)
  personita = pygame.image.load("gps6.png").convert_alpha() #cargar la img de la persona que se va a mover
  personita.set_colorkey([0, 0, 0])  #se usa para eliminar colores de la imagen (quitar imperfecciones/marcas de agua)
  pygame.mouse.set_visible(0)   #para que no se vea el raton al ejecutar el "juego"
  pygame.display.set_caption("Ubícate!") #nombre de la aplicación
  pygame.display.set_icon(personita)  # icono al abrir el maps
  while not cerrarGPS:  #buclee infinito del "juego", es decir, estar mostrando constantemente la posicion
    for event in pygame.event.get():     #si se detecta que se pulsa la X, se cierra el "juego", si no se pone esta opcion, no deja cerrarlo
      if event.type == pygame.QUIT:
        cerrarGPS = True
      if event.type == pygame.KEYDOWN:   #si se presiona la tecla escape, se cerrará la app Estás aquí! (nuestro GPS)
               if event.key == pygame.K_ESCAPE:
                     cerrarGPS = True
    coordenadaX, coordenadaY, UTMZoneNumber, direccion = posicion
    coordenadaX = abs(punto0X - coordenadaX)
    coordenadaY = abs(punto0Y - coordenadaY)
    Xpintado = (coordenadaX * 1920) /1298.02
    Ypintado = (coordenadaY * 1080) /807.68
    pantalla.fill((0, 0, 0))   #rellenar la pantalla por defecto, al aplicar un fondo creo q no es necesario poner esto, igual si se reescala mal q se rellenen dichos espacios con un color predefinido (negro creo q es mejor)
    pantalla.blit(imagen, [0, 0])  # mostramos la imagen de la etsisi+insia por pantalla
    pantalla.blit(personita, [Xpintado, Ypintado])  #mostramos sobre la imagen de fondo un icono que será nuestro receptor GPS
    pygame.display.update()  # actualiza la pantalla
    clock.tick(60)  #controlo los FPS de mi imagen
  pygame.quit()      #cerramos pygame

#------------------------------------ Codigo pincipal -------------------------------------------------------------#
while serialPort.isOpen():
 hilo1=threading.Thread(target=listener,args=(lock,),name='Listener')
 hilo1.start()
 hilo1.join()
 hilo2=threading.Thread(target=caster,args=(mensajeOriginal,lock,),name='Caster')
 hilo2.start()
 hilo2.join()
 hilo3 = threading.Thread(target=mostrarPunto, args=(posicion, lock,), name='MostrarPunto')
 hilo3.start()
 hilo3.join()
 
