#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import sqlite3

continue_reading = True


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    #print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()



def add_access_gate1(uid):
    conn=sqlite3.connect("useraccess.db")
    cursor=conn.cursor()
    uid1=''.join(str(e) for e in uid)
    #print uid1
    #print "check  for the uid and gate access  and give error here itself"
    cursor.execute("SELECT  id,gate1,gate2,device,currentdate,currenttime FROM gatepass WHERE device =%s" % uid1 )
    data=cursor.fetchone()
    #print data
 
    if data is None:
	cursor.execute("INSERT INTO gatepass(gate1,gate2,currentdate,currenttime,device) values(1,0,date('now'),time('now'), %s)" % uid1)
	conn.commit()
	conn.close()
	print "Gate:1 Access Granted"
    else:
	print "Gate:1 Access Denied"
        #print data[1]
 	#print data[2]
	if  (data[1] == 1):
		if (data[2] == 0) :
                    print("Gate:1  has been Accessed at Date: %s  Time: %s  Gate:2 not Accessed" % (data[3]  , data[4]))
                else:
		    print("Gate:2  has been Accessed at Date: %s  Time: %s  Gate 1 & 2 Both  Accessed" % (data[3], data[4]))


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
#print "Welcome to the MFRC522 data read example"
#print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    # if status == MIFAREReader.MI_OK:
    #    print  TagType

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        #print "Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])

        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
           # MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
            print "Access Card Valid"
            add_access_gate1(uid)
	else:
            print "Authentication error"

