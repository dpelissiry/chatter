import socket
import argparse
import sys
import re
import threading

class Request:
    CONNECT = 0
    MESSAGE = 1
    QUIT = 2

class Client():
    def __init__(self, id, server_ip):
        self.id = id
        self.port = 0
        self.ip = socket.gethostbyname(socket.gethostname())
        self.server_ip = server_ip.split(":")[0]
        self.server_port = int(server_ip.split(":")[1])

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.ip,self.port))

        #connect to the server
        try:
            self.s.connect((self.server_ip, self.server_port))
            
        except socket.error as err:
            print(f"socket failure: {err }")

    def parse_http(self, s):
        connack_pattern = "CONNACK\\r\\n\\r\\n"
        messageack_pattern = "MESSAGEACK\\r\\n\\r\\n"
        message_pattern = "MESSAGE\\r\\n.+: (?P<id>.*)\\r\\n.+: (?P<msg>.*)\\r\\n\\r\\n"
        quit_pattern = "QUIT\\r\\n\\r\\n"
        if re.match(quit_pattern, s): # first check if it is a quit message
            self.recv_quit()
            return
        elif re.match(connack_pattern, s):
            return True
        elif re.match(messageack_pattern, s):
            return True
        elif (res := re.match(message_pattern, s)):
            self.message_recv(res.groupdict())
            return True
                
            

    def run(self):
        self.server_connect(Request.CONNECT)
        self.receive_thread = threading.Thread(target=self.server_listen)
        self.receive_thread.start()
        for line in sys.stdin:
            line = line.rstrip()
            if line == '/quit':
                #tell client im quitting
                self.cmd_quit()
                break
            self.server_connect(Request.MESSAGE, line)

    def new_input(self, input):
        if input == '/quit':
            #tell client im quitting
            self.cmd_quit()
        self.server_connect(Request.MESSAGE, input)

    def message_recv(self, msg):
        print(f"{msg['id']}> {msg['msg']}")

    def server_listen(self):
        #open connection on self.port to wait for the partner to contact you
        while True:
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                break
            self.parse_http(data)
    

    def server_connect(self, r, data = None):
        #pass off a packet to the server
        
        try:
            if r == Request.CONNECT:
                self.s.send((f"CONNECT\r\nclientID: {self.id}\r\nIP: {self.ip}\r\nPort: {self.port}\r\n\r\n").encode('UTF-8'))
            elif r == Request.MESSAGE:
                self.s.send((f"MESSAGE\r\nclientID: {self.id}\r\nmessage: {data}\r\n\r\n").encode('UTF-8'))
            elif r == Request.QUIT:
                self.s.send((f"QUIT\r\nclientID: {self.id}\r\n\r\n").encode('UTF-8'))
                return
            #print(s.recv(1024).decode())
        except socket.timeout:
            print("Socket timeout:")
        except BrokenPipeError:
            print(f"Broken Pipe error")
        ack = self.s.recv(1024).decode('utf-8')
        server_connection_success = self.parse_http(ack)
        assert server_connection_success, "Failed to connect to server"
        return
    
    def cmd_quit(self):
        #inform server i am quitting to take me out of self.clients
        
        self.server_connect(Request.QUIT)
        self.s.close()
        #self.receive_thread.join()
        sys.exit("Chat session ended\nExiting program")
        
    def recv_quit(self):
        self.s.close()
        sys.exit(f"{self.partner['clientID']} ended the chat session\nExiting program")
        

    def __repr__(self):
        return f"Client {self.id}: {self.port}, {self.server_ip}:{self.server_port}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id')
    parser.add_argument('-p', '--port')
    parser.add_argument('-s', '--server')

    args = parser.parse_args()
    
    client = Client(args.id, args.server)
   # print(client)
    try:
        client.run()
    except KeyboardInterrupt:
        client.cmd_quit()
    

if __name__ == '__main__':
    main()
