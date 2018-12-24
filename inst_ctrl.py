#!/usr/bin/env python3

#       Conexion a instrumentos por medio de VISA
#       Arnulfo Zapata, Ing. Electronica
#       Instituto Tecnologico de Matamoros, Diseño de Sistemas de Prueba
#       Instalar la libreria visa: pip install -U pyvisa
#       Para ahorrar tiempo se puede establecer una frecuencia de barrido mas cerrada y una pantalla mas cerrada

import visa
import time

def delay(tempo):
    time.sleep(tempo)

res_man = visa.ResourceManager()
#lista de instrumentos disponibles
list_res = res_man.list_resources()

print('\n\tInstrument Connection v1.0\n')

conectar = raw_input('Conectar a los instrumentos? si/no: ')
if conectar == 'si':
        #generador, puede cambiar en la lista.
        generador = res_man.open_resource(list_res[2])
        #analizador
        analizador = res_man.open_resource(list_res[0])
        #caracter de terminacion del instrumento
        analizador.read_termination = '\r'
        analizador.write_termination = '\r'
        #baudrate
        analizador.baud_rate = 57600
        print("Generador de frecuencias conectado a: " + str(generador))
        print('Analizador de espectros conectado a: ' + str(analizador))
        print('\nConfiguracion del Generador de frecuencias...\n')
        freq_low = raw_input('Frecuencia de barrido baja en MHz: ')
        #frecuencias de barrido alta y baja
        generador.write('SOUR1:FREQ:STAR ' + freq_low + ' MHz')
        freq_high = raw_input('Frecuencia de barrido alta en MHz: ')
        generador.write('SOUR1:FREQ:STOP ' + freq_high + ' MHz')
        #encendido de marcador
        analizador.write('MEAS:MARK:ON 1')
        #Peak hold
        analizador.write('MEAS:TRA 1 2')
        #Configuracion de pantalla del analizador
        analizador.write('MEAS:FREQ:ST 50 MHz')
        analizador.write('MEAS:FREQ:STP 220 MHz')
        delay(2)
        print('Ajustando a inf reps...')
        #se repite el proceso infinitamente
        generador.write('SOUR1:SWE:coun INF')
        delay(3)
        print('Ajustando barrido con 100 puntos...')
        #Resolucion de barrido de 100 puntos
        generador.write('SOUR1:SWE:poin 100')
        delay(3)
        #Ajuste de tiempo de 50 ms
        generador.write('SOUR1:SWE:DWELl 50.000000E-03')
        delay(3)
        #MODO SWEEP E INICIO DE RF
        generador.write('SOUR1:FREQ:MODE SWE')
        generador.write('OUTP1:STAT ON') #<== TIENE QUE SER USADO 
        # Empieza el barrido
        print('\nConfiguracion del analizador de espectros...\n')
        delay(7)
        print('\nMarcador 1: Activado')
        #Amplitud en dBm
        analizador.write('MEAS:REFL:UNIT 1')
        #Referencia en 0 dBm
        analizador.write('MEAS:REFL 0')
        delay(7)
        #marcador al pico
        analizador.write('MEAS:MARK:TOPEAK 1')
        delay(2)
        #amplitud del pico para sacar el corte (-3dBm)
        level1 = analizador.query('MEAS:MARK:NORM:LEVEL 1?')
        level1 = level1[:-4]
        level1 = float(level1)
        level_cte1 = level1-3
        analizador.write('meas:refl '+str(level_cte1))
        #ajustar referencia a freq_cte
        analizador.write('MEAS:MARK:TOST 1')
        analizador.write('MEAS:FREQ:ST 90 MHz')
        delay(7)      
        analizador.write('MEAS:MARK:TOPEAK 1')
        delay(1)
        frec_cte1 = analizador.query('MEAS:MARK:NORM:FREQ 1?')
        frec_cte1 = frec_cte1[:-4]
        #####FRECUENCIA DE CORTE LOW
        frec_cte1 = float(frec_cte1)

        analizador.write('MEAS:MARK:tostp 1')
        #Ajustar la frecuencia de stp por que se desajusta al mandar a la frecuencia final
        analizador.write('MEAS:FREQ:STP 220 MHz')
        delay(9)
        analizador.write('MEAS:MARK:TONPL 1')
        delay(3)
        frec_cte2 = analizador.query('MEAS:MARK:NORM:FREQ 1?')
        frec_cte2 = frec_cte2[:-4]
        #####FRECUENCIA DE CORTE HIGH
        frec_cte2 = float(frec_cte2)
        ancho_banda = frec_cte2 - frec_cte1
        print('Ancho de banda: '+str(ancho_banda) + ' MHZ')
        frec_cen = (abs(ancho_banda)/2) + abs(frec_cte1)
        print('Frecuencia Central: ' + str(frec_cen) + ' MHz')
        print('Frecuencia de cte L: ' + str(frec_cte1)+ ' MHZ')
        print('Frecuencia de cte H: ' + str(frec_cte2)+ ' MHZ')
        analizador.write('MEAS:TRA 1 1')
        generador.write('OUTP1:STAT OFF')
