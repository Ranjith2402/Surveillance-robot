import socket
import time

ip = socket.gethostbyname(socket.gethostname())
print(ip)

server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

server.bind((ip, 99))

server.listen(3)

while True:
    client, address = server.accept()
    print(client, address)
    text = client.recv(1024).decode().replace('\r\n', '\n').strip()
    print(text)
    if text == 'HANDSHAKE' or text == 'RESEND':
        client.send('HELLO'.encode('utf-8'))
        time.sleep(15)
        client.send('ALERT:FIRE:smoke was detected, your house is totally f***ed up. Bye'.encode('utf-8'))
        print('Data sent')
