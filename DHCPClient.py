#####################
# Oscar Lugo
# CS436 
# Project 1
#

from socket import *
import re,uuid

#socket configuration
serverName = 'localhost'
serverPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)

MyMAC = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def main():
    startMessage = input("Press Enter to Start\n")
    messageWMac = "Client: DISCOVER%" + MyMAC
    print(messageWMac)
    clientSocket.sendto(messageWMac.encode(),(serverName, serverPort))
    while 1:
        returnedMessage, serverAddress = clientSocket.recvfrom(2048)
        returnedMessageDecoded = returnedMessage.decode()
        print(returnedMessageDecoded)
        if "OFFER" in returnedMessageDecoded:
            OfferRecv(returnedMessageDecoded, serverAddress)
        elif "DECLINE" in returnedMessageDecoded:
            print("Network is all occupied, terminating")
            quit()
        elif "ACKNOWLEDGE" in returnedMessageDecoded:
            AckRecv(returnedMessageDecoded,serverAddress)
        elif "ALREADYINNETWORK" in returnedMessageDecoded:
            AlreadyInNet(serverAddress)
        else:
            print("Invalid Message received from DHCPServer")
            quit()

#####################
# Handle OFFER from server 
# Check MAC address returned matches my address
#        
def OfferRecv(message, sAddress):
    #print("Debug: offmsg " + message)
    separatedMessage = message.split('%')
    macOnly = separatedMessage[1]
    #print("Debug MAC: " + macOnly)
    IPOnly = separatedMessage[2]
    if MyMAC.upper() == macOnly.upper():  # Check MAC Address match
        offerFound = "Client: REQUEST%"+ macOnly+'%'+IPOnly
        print(offerFound)
        clientSocket.sendto(offerFound.encode(),(serverName, serverPort))
    else:
        print("Incorrect MAC found on offer msg")

#####################
# Handle ACKNOWLEDGE message received from Server
# Connected to network, print message
#
def AckRecv(message, sAddress):
    separatedMessage = message.split('%')
    macOnly = separatedMessage[1]
    IPOnly = separatedMessage[2]
    print("SUCESS "+macOnly + " now connected using " + IPOnly)
    #clientSocket.close()
    AlreadyInNet(sAddress)

#####################
# Handle Aready in Network receied from Server,
# print menu allowing Client to choose an action
#
def AlreadyInNet(sAddress):
    valid = False
    while not valid:
        selectAction = input("Make a Selection \n" +
            "\n1. release \n2. renew \n3. Quit\n")
        #print("Debug: Selection " + selectAction)
        if selectAction == "1":
            valid = True
            release = "Client: RELEASE%"+ MyMAC
            print(release)
            clientSocket.sendto(release.encode(),(serverName, serverPort))
        elif selectAction == "2":
            valid = True
            renew = "Client: DISCOVER%"+ MyMAC
            print(renew)
            clientSocket.sendto(renew.encode(),(serverName, serverPort))
        elif selectAction == "3":
            valid = True
            print("Quitting at Client Request")
            quit()
        else:
            print("Invalid selection, select 1-3")
            valid = False

if __name__ == '__main__':
    main()