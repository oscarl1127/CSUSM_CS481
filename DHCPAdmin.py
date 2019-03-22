#####################
# Oscar Lugo
# CS436 
# Project 1
# Ectra credit - get Active Network from Server

from socket import *

serverName = 'localhost'
serverPort = 12001
adminSocket = socket(AF_INET, SOCK_DGRAM)

def main():
    print("ACTIVE NETWORK IS AS FOLLOWS:\n")
    activeNetRequest = "ADMINALL"
    adminSocket.sendto(activeNetRequest.encode(), (serverName, serverPort))

    returnedMessage, serverAddress = adminSocket.recvfrom(2048)
    returnedMessageDecoded = returnedMessage.decode()
    print(returnedMessageDecoded)

if __name__ == '__main__':
    main()