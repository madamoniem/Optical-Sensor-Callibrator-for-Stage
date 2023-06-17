#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 22:10:08 2020
@author: jgollub
"""
import serial
from time import sleep
from zaber_motion.ascii import Connection
from zaber_motion import Units, MotionLibException

# configure the serial connection
#check for usb rs232 serial connection using command line: ls /dev/cu.*

class SyringePump:
    '''
    syringe commands for infusion or withdraw
    syringe_command(ser,0, 'DIR INF', print_to_screen=True)
    syringe_command(ser,0, 'DIR WDR', print_to_screen=True)
    
    start/stop commands
    syringe_command(ser,0, 'RUN', print_to_screen=True)
    syringe_command(ser,0, 'STP', print_to_screen=True)
    '''
    def __init__(self, port: str = 'COM5'):
        self.connection = serial.Serial(
                                     port= port,
                                     baudrate=19200,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     bytesize=serial.EIGHTBITS,
                                     timeout=.1
                                     )
         
    def __enter__(self):

        return self

    def syringe_command(self, pump_number: float, command, print_to_screen: bool=False):
        self.connection.write(((f'{pump_number:02d}' + command + '\r')).encode('utf-8'))

        response=self.connection.readline() 
        (address, status, data)=(response.decode('utf-8')[1:-1][:2],
                                 response.decode('utf-8')[1:-1][2:3],
                                 response.decode('utf-8')[1:-1][3:])
        
        if print_to_screen is True:
            print(f'Syringe [{address}], (status: {status}), Response: {data}')
            
    def wait_for_stage(self, pump_number: float, print_to_screen: bool=True):
        
        while True:
            self.connection.write(((f'{pump_number:02d}' + '' + '\r')).encode('utf-8'))
             
            response=self.connection.readline() 
            (address, status, data)=(response.decode('utf-8')[1:-1][:2],
                                     response.decode('utf-8')[1:-1][2:3],
                                     response.decode('utf-8')[1:-1][3:])
        
            if print_to_screen is True:
                print(f'Syringe [{address}], (status: {status}), Response: {data}')
           
            if status is 'S':
                break
            
    def setup(self, pump_number: float, syringe_diameter: float, volume_step: float, rate: float):
         
        self.syringe_command(pump_number, ('DIA ' + str(syringe_diameter))) #set diameter
        self.syringe_command(pump_number, 'DIA ', print_to_screen=True)
        
        self.syringe_command(pump_number, 'VOL ML') #set volume units 
        self.syringe_command(pump_number, 'VOL ' + str(volume_step)) #set volume step size
        self.syringe_command(pump_number, 'VOL ', print_to_screen=True)

        self.syringe_command(pump_number, 'RAT ' + str(rate)) #set rate 
        self.syringe_command(pump_number, 'RAT ', print_to_screen=True)
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.connection.close()
        
class ZaberMultistaticStage:
    def __init__(self, port: str = 'COM6'):
        self.port = Connection.open_serial_port(port)
        
        device_list = self.port.detect_devices()
        print("Found {} devices".format(len(device_list)))
             
        self.maxHomingX_Sat1 = 20000 #steps/sec
        self.maxHomingY_Sat1 = 40000 #steps/sec 
        self.maxVelocity=10000
        # self.maxVelocity=100000
             
        device1 = device_list[0] # Device number 1  
    
        self.sat1_X_stage = device1.get_axis(2)   
        self.sat1_Y_stage = device1.get_axis(1)
            
        try:
        #set max axes speed for homing
            self.sat1_X_stage.settings.set('maxspeed', self.maxHomingX_Sat1)
            self.sat1_Y_stage.settings.set('maxspeed', self.maxHomingY_Sat1)  

        except MotionLibException as err:
            print(err) 

        try:
            # Home the device and check the result.
            self.sat1_X_stage.home()
            self.sat1_Y_stage.home()
      
        except MotionLibException as err:
            print(err)
            
        try:
            #set maxspeed for stage movement
            self.sat1_X_stage.settings.set('maxspeed', self.maxVelocity)
            self.sat1_Y_stage.settings.set('maxspeed', self.maxVelocity)    
        except MotionLibException as err:
            print(err) 
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.port.close() 

class Zaber_2axis_LST1500D:
    def __init__(self, port: str = 'COM8'):
        self.ser=serial.Serial()
        self.ser.port=port
        self.ser.timeout = 1
        self.ser.baudrate=115200
        self.ser.open()
                     
        # device1 = [0] # Device number 1  
        self.axes = '0'
        self.x_axis = '1'    
        self.y_axis = '2'
        
        self.step_size=1.984375*10**(-3) #convert to mm units
    
    def wait_for_idle_status(self):
        
        #test that x-axis has finished moving
        testx=-1
        while testx == -1:
            sleep(.02)
            self.ser.write(f'/{self.x_axis}\r'.encode())            
            reply_x=self.ser.read_until()
            testx=reply_x.decode().find('IDLE')
            # print(f'{reply_x.decode()}, and test is {testx}')
            if reply_x.decode().find('WR') != -1:
                print('x axis not homed')
            sleep(.1)
        
        #test that y-axis has finished moving
        testy=-1
        while testy== -1:
            sleep(.02)
            self.ser.write(f'/{self.y_axis}\r'.encode())
            reply_y=self.ser.read_until()            
            testy=reply_y.decode().find('IDLE')
            # print(f'{reply_y.decode()}, and test is {testy}')
            if reply_y.decode().find('WR') != -1:
                print('y axis not homed')
            sleep(.1) #set for long settle time
        
    def home_axes(self):

        self.ser.write('/0 home\r'.encode())
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        self.wait_for_idle_status()

    def move_x_absolute(self, position, quiet=True): #input in mm
        position_in_motor_steps =int(round(position/self.step_size,0))
        self.ser.write(f'/{self.x_axis} move abs {position_in_motor_steps}\r'.encode() )
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        if not quiet:
            print(f'set x_position= {position:.6g}')
            print(f'set x_position in steps= {position_in_motor_steps:.12g}')
        self.wait_for_idle_status()

        
    def move_y_absolute(self, position, quiet=True): #input in mm
        #note accounting for negative axis by subtracting 1500 mm
        position_in_motor_steps =int(round((position)/self.step_size,0))
        self.ser.write(f'/{self.y_axis} move abs {position_in_motor_steps}\r'.encode())
        dummy_reply=self.ser.read_until() #throw away response so wait for stage command works properly
        if not quiet:
            print(f'set y_position= {position:.6g}')
            print(f'set y_position in steps= {position_in_motor_steps:.12g}')
        self.wait_for_idle_status()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self.ser.close()     