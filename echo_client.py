import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 18000)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    message = input('input a message: ')
    print('sending "%s"' % message)
    message = message.encode()
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(64)
        amount_received += len(data)
        print('received "%s"' % data.decode())

finally:
    print('closing socket')
    sock.close()
