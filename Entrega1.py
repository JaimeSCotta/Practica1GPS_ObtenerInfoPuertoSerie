import serial
import utm
import threading

serialPort = serial.Serial(port = "COM3", baudrate=4800,
                           bytesize=serial.EIGHTBITS, timeout=1, stopbits=serial.STOPBITS_ONE)
lock=threading.Lock() 
mensajeOriginal = bytearray(200)
cabecera = bytearray(6)
posicion = tuple()

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


while serialPort.isOpen():
 hilo1=threading.Thread(target=listener,args=(lock,),name='Listener')
 hilo1.start()
 hilo1.join()
 hilo2=threading.Thread(target=caster,args=(mensajeOriginal,lock,),name='Caster')
 hilo2.start()
 hilo2.join()
 
