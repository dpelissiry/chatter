import tkinter as tk
from client import Client
import threading
import argparse
import sys

def main():
    root = tk.Tk()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id')
    #parser.add_argument('-s', '--server')
    args = parser.parse_args()
    client = Client(args.id)#, args.server)
    root.title(f'{args.id} @ {client.ip}:{client.port}')
    #client.run()

    try:
        threading.Thread(target=client.run).start()
    except KeyboardInterrupt:
        client.cmd_quit()
    
    receive_frame = tk.Frame(root)
    receive_frame.pack(side="top")
    display = tk.Text(receive_frame)
    display.pack(side="bottom")
    threading.Thread(target=query_queue,args=(display, client)).start()
    

    send_frame = tk.Frame(root, padx=10,pady=10)
    send_frame.pack(side="bottom")
    entry = tk.Entry(send_frame)
    entry.pack(side="top", fill="x", padx=10, pady=10)
    
    button_send = tk.Button(send_frame, text='Send', width=25, command=lambda: send_message(entry, client))
    button_send.pack(side="right", padx=10, pady=10)

    button_quit = tk.Button(send_frame, text='Disconnect', width=25, command=lambda: quit_client(client,root))
    button_quit.pack(side="right", padx=10, pady=10)
    root.mainloop()
    

def quit_client(client,r):
    threading.Thread(target=client.cmd_quit).start()
    r.destroy()
    sys.exit()

def send_message(entry, client):
    message = entry.get()
    if message:
        # Move the long-running task to a separate thread
        threading.Thread(target=client.new_input, args=(message,)).start()
        entry.delete(0, 'end')
def query_queue(display,client):
    while True:
        if (msg := client.get_message()):
            t = msg['type']
            if t == 'msg':
                display.insert(tk.END, (f"{msg['id']}> {msg['msg']}\n"))
            elif t == 'quit':
                display.insert(tk.END, (f"{msg['id']} has disconnected.\n"))


if __name__ == "__main__":
    main()
