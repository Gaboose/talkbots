import socket, sys, time

# To listen to packets use:
# nc -ul IP -p PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
IP, PORT = sys.argv[1], sys.argv[2]

while True:
    sock.sendto(bytes('labas\n', 'utf-8'), (IP, int(PORT)))
    time.sleep(1)