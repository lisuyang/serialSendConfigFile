#!/usr/bin/env python27
# -*- coding: utf-8 -*-

' an USB test '

__author__ = 'Suyang Li'

import time, threading
import string
import serial
import serial.tools.list_ports
from time import sleep
from functools import reduce
from enum import Enum
from serial.serialutil import portNotOpenError

CheckStatus = 'none'
ReadBuff = ""
comList = []
def checkPort(portList):
	global CheckStatus
	global comList

	CheckStatus = False
	checkSerial = serial.Serial(port=portList, baudrate=9600)
	readCheckThread = threading.Thread(target=readData, name='readCheckDataThread', args=(checkSerial,))
	readCheckThread.start()
	result = sendData("123over\r\n",checkSerial,False)
	sleep(0.1)
	if result and CheckStatus:
		comList.append(portList)
		print ("This port is MCU port")


	checkSerial.cancel_write()
	checkSerial.cancel_read()
	readCheckThread._delete()

	checkSerial.close()
	print ("checkSerial.close")


RWThreadLock = False
#设置端口和波特率
def readData(serial):
	readStr = []
	global RWThreadLock
	global CheckStatus
	global ReadBuff
	print ("Serial is reading...")
	try:
		while True:
			readChar = serial.read(1)
			RWThreadLock = False
			readStr.append(readChar.decode("utf-8"))
			# print (readChar)
			if (readChar == b'\n'):
				readStr = reduce(lambda x,y:str(x) + str(y),readStr)
				ReadBuff = str(ReadBuff) + str(readStr)
				if readStr == "clear\r\n" or len(ReadBuff) > 1000:
					ReadBuff = ""
				if readStr =="123over\r\n":
					CheckStatus = True
					pass
				if readStr == "successful\r\n":
					print ("%s config successfully" %serial.name)

				print (readStr)
				print (ReadBuff)
				readStr = []
	except AttributeError as e:
		pass
	except TypeError as e:
		pass


def sendData(indata,serial,anotherLine):
	global RWThreadLock
	global CheckStatus
	if anotherLine:
		indata += "\r\n"
	timeoutCnt = 0
	# indata = "led 1 off\r\n"
	for x in indata.encode():
		serial.write(chr(x).encode())
		RWThreadLock = True
		while RWThreadLock:
			# print ("timeoutCnt:%d"  %timeoutCnt)
			timeoutCnt += 1
			if timeoutCnt > 1000:
				CheckStatus = False
				print ("This port can't receive data!")
				return False
			sleep(0.001)
	return True

def sendFile(serial):
	try:
		ConfigFile = open("range.py",'r')
		FileInformation = ConfigFile.readlines()
		for information in FileInformation:
			sendData(information,serial,False)
			# sleep(0.01)
			pass
		pass
	finally:
		if ConfigFile:
			ConfigFile.close()


def writeData(serial):
	writeStr = ""
	print ("You can write data into serial")
	while True:
		writeStr = input()
		result = sendData(writeStr,serial,True)


readThread = list()
writeThread = list()
port_list = list(serial.tools.list_ports.comports())
if len(port_list) == 0:
	print ("The PC doesn't have any port")
else:
	[checkPort(port_list[i].device) for i in range(0,len(port_list))]
for i in range(0,len(comList)):
	print ("open %s port" % comList[i])
	serial = serial.Serial(port=comList[i], baudrate=9600)

	readDataThreadName = 'readDataThread' + comList[i]
	# writeDataThreadName = 'writeDataThread' + comList[i]
	print (readDataThreadName)
	# print (writeDataThreadName)
	readThread = threading.Thread(target=readData, name=readDataThreadName, args=(serial,))
	# writeThread = threading.Thread(target=writeData, name=writeDataThreadName, args=(serial,))

	readThread.start()
	# writeThread.start()
	# readThread.join()
	# writeThread.join()

	# sendFile(serial)
	# sendData("sadf\r\n",serial,False)
	serial.cancel_write()
	serial.cancel_read()
	readThread._delete()

	serial.close()

print ("all threads have over!")

#for char in cmd1.encode():
#	s.write (chr(char).encode())

# except BaseException as e:
# 	# print ("BaseException")
# 	pass
	# for i in range(0, len(comList)):
	# 	serial[i].close()
	# 	print ("%s com port" %comList[i])
