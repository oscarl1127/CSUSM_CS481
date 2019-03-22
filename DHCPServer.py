#####################
# Oscar Lugo
# CS436 
# Project 1
#

from socket import *
import ipaddress
import ast

IPaddresssesAvailable = list(ipaddress.IPv4Network('192.168.1.0/24'))
ActiveNetwork = {"NETID": str(IPaddresssesAvailable[0]), 
"BROADCAST" : str(IPaddresssesAvailable[-1]) }  

NetworkDb = dict()

del IPaddresssesAvailable[0] # remove NETID from range
del IPaddresssesAvailable[-1] # remove Brodacast from range

# Socket Configuration
serverPort = 12001 # Randomly selected Port 
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))

def main():
    print ('The server is ready to receive')
    while 1:
        message, clientAddress = serverSocket.recvfrom(2048) 
        modifiedMessage = message.decode().upper()
        print(modifiedMessage)
        if "DISCOVER" in modifiedMessage :
            ServerDiscover(modifiedMessage, clientAddress)
        elif "REQUEST" in modifiedMessage:
            ServerRequest(modifiedMessage, clientAddress)
        elif "RELEASE" in modifiedMessage:
            ReleaseRequest(modifiedMessage, clientAddress)
        elif "RENEW" in modifiedMessage:
            ReneweRequest(modifiedMessage, clientAddress)
        elif "ADMINALL" in modifiedMessage:
            adminRequestAll(modifiedMessage, clientAddress)
        else:
            print("Invalid Message received from DHCPClient")
            quit()

########
# Handler DISCOVER received from Client
# IF Client already in Active network reply ALREADYINNETWORK  
# IF No available IP then reply DECLINE
# IF Precious record exist for MAC address , OFFER with prev used IP if available
# No previous checbked condition met, OFFER next available IP
####
def ServerDiscover(message, cAddress):
    maconly = message.split('%') # clean for MAC address only
    #print("Debug Maconly "+ maconly[1])
    if maconly[1] in ActiveNetwork: # Client already in Network
        print("Server: Client " + maconly[1] + " already in Network")
        AlreadyInNetMssg = "ALREADYINNETWORK"+ maconly[1]
        serverSocket.sendto(AlreadyInNetMssg.encode(), cAddress)   
    elif len(IPaddresssesAvailable) == 0: # if IP pool is fully occupied
        IPFull = "Server: DECLINE, Terminating system"
        serverSocket.sendto(IPFull.encode(), cAddress)
        quit()
    elif maconly[1] in NetworkDb:  #Check records to see if IP previously assigned
        print("Client " + maconly[1] + " previous IP " + NetworkDb[maconly[1]] )
        if NetworkDb[maconly[1]] in IPaddresssesAvailable:  # Offer prev used IP
            offerMessage = "Server: OFFER%" +maconly[1]+'%' + NetworkDb[maconly[1]]
            print(offerMessage)
            serverSocket.sendto(offerMessage.encode(), cAddress)
        else: #Offer Next Available
            availableIP = IPaddresssesAvailable[0] # Next available IP
            offerIPMessage = "Server: OFFER%" + maconly[1] +"%"+ str(availableIP)
            print(offerIPMessage)
            serverSocket.sendto(offerIPMessage.encode(), cAddress) 
    #if IP Pool not fully occupied and MAC not previously assigned
    else:
        availableIP = IPaddresssesAvailable[0] # Next available IP
        offerIPMessage = "Server: OFFER%" + maconly[1] +"%"+ str(availableIP)
        print(offerIPMessage)
        serverSocket.sendto(offerIPMessage.encode(), cAddress)

#####################
# Handle REQUEST from Client
# IF IP prev offered is still available, accept requet 
#   NOT available OFFER again with next available IP
#
def ServerRequest(message, cAddress):
    #print("Debug: " + message)
    separatedMessage = message.split('%')
    macOnly = separatedMessage[1]
    #print("Debug MAC: " + macOnly)
    IPOnly = separatedMessage[2]
    #print("Debug IP: " + IPOnly)
    #If IP offered is still available
    if ipaddress.IPv4Address(IPOnly) in IPaddresssesAvailable:
        #print("DEbug: IP still available")
        IPaddresssesAvailable.remove(ipaddress.IPv4Address(IPOnly)) #Remove from available IP addresses
        ActiveNetwork[macOnly] = IPOnly # add to ActiveNetwork
        NetworkDb[macOnly] = IPOnly # add to MAC Addres IP record
        AckMessage = "Server: ACKNOWLEDGED%" +macOnly +'%' +IPOnly
        print(AckMessage)
        serverSocket.sendto(AckMessage.encode(), cAddress)  
    else:  # If not available anymore, offer first available IP
        print("Not available anymore")
        availableIP = IPaddresssesAvailable[0] # Next available IP
        offerIPMessage = "Server: OFFER%" + macOnly +"%"+ str(availableIP)
        print(offerIPMessage)
        serverSocket.sendto(offerIPMessage.encode(), cAddress)

#####################
# Handle RELEASE message from Client
# Remove from active network and re add to available IP List
#
def ReleaseRequest(message, cAddress):
    maconly = message.split('%') # clean for MAC address only
    #print("Debug Maconly "+ maconly[1])
    #Remove from Active Network
    if maconly[1] in  ActiveNetwork:
        #Re add to Avilable IPs list
        IPaddresssesAvailable.insert(0, ipaddress.IPv4Address( ActiveNetwork[maconly[1]]) )
        del ActiveNetwork[maconly[1]] # Remove from active Network
        print("Client " + maconly[1] + " Removed from Network")
        AlreadyInNetMssg = "ALREADYINNETWORK" + maconly[1]
        serverSocket.sendto(AlreadyInNetMssg.encode(), cAddress)
    else:
        print("Error, MAC Not found")

#####################
# Handle RENEW received from Client
# Send OFFER with next available IP
#
def ReneweRequest(message, cAddress):
    maconly = message.split('%') # clean for MAC address only
    #print("Debug Maconly "+ maconly[1])
    #Re add from Active Network
    availableIP = IPaddresssesAvailable[0] # Next available IP
    offerIPMessage = "Server: OFFER%" + maconly[1] +"%"+ str(availableIP)
    print(offerIPMessage)
    serverSocket.sendto(offerIPMessage.encode(), cAddress) 

#####################
# Handle Admin request to List Active network
#
def adminRequestAll(message, cAddress):
    payloadStr = str(ActiveNetwork)
    serverSocket.sendto(payloadStr.encode(), cAddress)


if __name__ == '__main__':
    main()