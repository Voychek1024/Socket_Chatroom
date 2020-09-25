import socket

TCP_IP = '192.168.1.112'
TCP_PORT = 18443
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
with open('received_file.txt', 'wb') as f:
    print('file opened')
    while True:
        print('receiving data...')
        data = s.recv(BUFFER_SIZE)
        if not data:
            f.close()
            print('file closed')
            break
        f.write(data)

print('Successfully get the file')
s.close()
print('connection closed')