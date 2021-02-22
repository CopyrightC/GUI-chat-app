import socket, threading
host = '0.0.0.0'
port = 65432
clients = []
names = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()


def sendall(msg): 
    for client in clients:
        client.send(msg)


def recv_broadcast(client):
    while True:
        try:
            msg1 = client.recv(1024)
            sendall(msg1)
        except:
            cd_in = clients.index(client)
            clients.pop(cd_in)
            client.close()
            print(f"{names[cd_in]} left the chat!")
            sendall(f"{names[cd_in]} left the chat!".encode())
            names.pop(cd_in)
            break


def main():
    print("Server is listening on port {} and ip {}".format(port,host))
    while True:
        conn,addr = s.accept()
        print("connected by ", addr)
        conn.send("usr".encode())
        client_name = conn.recv(1024)
        names.append(client_name)
        clients.append(conn)
        print(client_name)
        sendall(f"{client_name} joined the chat! \n".encode())
        conn.send("You joined the chat! \n".encode())
        thread = threading.Thread(target=recv_broadcast,args=(conn,))
        thread.start()


main()
