import socket
import sys
import argparse
import re
import threading
from queue import Queue

class Request:
    MESSAGE = 0
    CONNACK = 1
    QUIT = 2
    QUITACK = 3

class Server():
    def __init__(self):
        self.port = 5555#int(port)
        self.ip = "0.0.0.0"
        self.messages = Queue()
        self.clients = []#Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip,self.port))
        # threading.Thread(target=self.listen, daemon=True).start()
        # threading.Thread(target=self.send,daemon=True).start()

    def parse_http(self, s, conn = None):
        connect_patt = "CONNECT\\r\\n.+: (?P<id>.+)\\r\\n.+: (?P<ip>.+)\\r\\n.+: (?P<port>.+)\\r\\n\\r\\n"
        message_patt = "MESSAGE\\r\\n.+: (?P<id>.+)\\r\\n.+: (?P<msg>.+)\\r\\n\\r\\n"
        quit_patt    = "QUIT\\r\\n.+: (?P<id>.+)\\r\\n\\r\\n"
        print(s)
        if (res := re.match(connect_patt, s)) is not None:
            self.new_conn(conn, res['id'])
        elif (res := re.match(message_patt, s)) is not None:
            self.new_message(res.groupdict(), res['id'])
        elif (res := re.match(quit_patt, s)) is not None:
            self.delete_user(res['id'], conn)
        return
    def delete_user(self, id, conn):
        self.send(Request.QUITACK,None, conn)
        for n, d in enumerate(self.clients):
            if id == d['id']:
                print(f"{id} has disconnected")
                del self.clients[n]
                break
        self.send(Request.QUIT, id) # inform other users that user quit
        return


    def new_conn(self, conn, id):
        self.clients.append({'id':id, 'conn':conn})
        print(f"{id} has connected!")
        self.send(Request.CONNACK, None, conn)
        return
    
    def new_message(self, data, id):
        self.messages.put(data)
        self.send(Request.MESSAGE, data, id)

    def listen(self):        
        print(f"Listening on {self.ip}:{self.port}")
        self.socket.listen()
        while True:
            conn, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(conn,)).start()
           # self.parse_http(data, conn)
    def handle_client(self, conn):
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break
            self.parse_http(data, conn)

    def send(self, r, data = None, conn = None):
        # while True:
        #     for m in self.messages():
        if r == Request.MESSAGE:
            for c in self.clients:
                conn_obj = c['conn']
                if c['id'] == conn: #send messack back to sender
                    conn_obj.send((f"MESSAGEACK\r\n\r\n").encode('utf-8'))
                    continue
                conn_obj.send((f"MESSAGE\r\nid: {data['id']}\r\nmsg: {data['msg']}\r\n\r\n").encode('utf-8'))
                #ack = self.socket.recv(1024).decode('utf-8')
                
        elif r == Request.CONNACK:
            conn.send((f"CONNACK\r\n\r\n").encode('utf-8'))
        elif r == Request.QUIT:
            print("SENDING QUIT")
            for c in self.clients:
                conn_obj = c['conn']
                conn_obj.send((f"QUIT\r\nid: {data}\r\n\r\n").encode('utf-8'))
                #ack = self.socket.recv(1024).decode('utf-8')
        elif r == Request.QUITACK:
            conn.send((f"QUITACK\r\n\r\n").encode('utf-8'))
        return

    
    def quit(self):
        self.socket.close()
        sys.exit()

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-p', '--port')

    # args = parser.parse_args()
    server = Server()
    server.listen()
if __name__ == '__main__':
    main()