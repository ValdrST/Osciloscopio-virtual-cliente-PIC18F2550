import serial
import sys
import glob
import numpy as np
from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
x_val = []
y_val_an0 = []
y_val_an1 = []
index = count()
def serial_ports():
    """ Enlista todos los puertos seriales disponibles

        :raises EnvironmentError:
            Cuando el sistema operativo no es compatible
        :returns:
            Una lista con los puertos seriales del sistema
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

""" Recibe los datos generados por el puerto serial y los convierte a voltaje
        Hace un calculo basandose en su resolucion de 8 bits 1/255 (CTE_bits)
        CTE_Volts es el voltaje maximo que permite leer el controlador
"""
def graficacion(dato1, dato2):
    CTE_bits = 1/255
    CTE_Volts = 5.0
    dato1 = (dato1 * CTE_bits) * CTE_Volts
    dato2 = (dato2 * CTE_bits) * CTE_Volts
    print("AN0:{0} AN1:{1}".format(dato1,dato2))
    x_val.append(next(index))
    y_val_an0.append(dato1)
    y_val_an1.append(dato2)
    if len(x_val) > 20:
        x = x_val[-20:]
        y_an0 = y_val_an0[-20:]
        y_an1 = y_val_an1[-20:]
    else:
        x = x_val
        y_an0 = y_val_an0
        y_an1 = y_val_an1
    ax.clear()
    ax.set_ylabel('Voltaje [V]')
    ax.set_xlabel('Muestras')
    plt.ylim(-1,6)
    plt.grid()
    plt.title("Osciloscopio con PIC18F2550") 
    ax.grid(True)
    ax.set_title("Osciloscopio virtual con PIC18F2550")
    ax.set_ylim(-1,6)
    ax.set_xlim(x[0],x[len(x)-1])
    ax.plot(x,y_an0,label="AN0 = {0}[V]".format(round(dato1,5)))
    ax.legend(shadow=True)
    ax.plot(x,y_an1,label="AN1 = {0}[V]".format(round(dato2,5)))
    ax.legend(shadow=True, fancybox=True, loc='upper left')
""" Hace la lectura del puerto serial
    Convierte los datos de hexadecimal a decimal
"""
def data_gen(port,baudrate):  
    ser = serial.Serial(port,baudrate=baudrate)  
    print(ser.baudrate)
    while(True):
        x = ser.read()
        if(x.hex() == '55'):
            dato1 = ser.read()
            dato2 = ser.read()
            dato1 = int(dato1.hex(),16)
            dato2 = int(dato2.hex(),16)
            graficacion(dato1,dato2)
            break
    ser.close()

def update(i,port,baudrate):
    
    data_gen(port,baudrate)



if __name__ == "__main__":
    fig, ax = plt.subplots()
    parser = argparse.ArgumentParser()
    parser.add_argument("-l","--list-ports", help="lista los puertos COM disponibles",action="store_true",default=False)
    parser.add_argument("-p","--port",help="El puerto COM del cual se hara la conexion ejemplo -p COM5")
    parser.add_argument("-b","--baudrate",help="el Baudrate con el que trabajara el puerto serial. Ejemplo -b 9600", default= 921600)
    args = parser.parse_args()
    if(args.list_ports):
        print(serial_ports())
    else:
        port = args.port
        baudrate = args.baudrate
        print(port)
        print(baudrate)
        ser = serial.Serial(port,baudrate=baudrate)
        ani = FuncAnimation(fig,update,fargs=(port,baudrate),interval=1)
        plt.show()