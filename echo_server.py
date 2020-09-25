import sys
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 18000)
print("starting up on %s port %s" % server_address)
sock.bind(server_address)

sock.listen(1)
while True:
    print("waiting for a connection...")
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        while True:
            data = connection.recv(64)
            if data:
                print('received "%s"' % data.decode())
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no more data from', client_address)
                break
    finally:
        # Clean up the connection
        connection.close()
