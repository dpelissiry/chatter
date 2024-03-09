import tkinter as tk
from client import Client
import threading

def main():
    root = tk.Tk()
    root.title('Chat Client')

    client = Client("Dylan", "DYLAN-LAPTOP:5557")

    try:
        threading.Thread(target=client.run).start()
    except KeyboardInterrupt:
        client.cmd_quit()

    entry = tk.Entry(root)
    entry.pack(side="bottom", fill="x", padx=10, pady=10)

    button_send = tk.Button(root, text='Send', width=25, command=lambda: send_message(entry, client))
    button_send.pack(side="bottom", padx=10, pady=10)

    button_quit = tk.Button(root, text='Disconnect', width=25, command=client.cmd_quit)
    button_quit.pack(side="bottom", padx=10, pady=10)

    root.mainloop()

def send_message(entry, client):
    message = entry.get()
    if message:
        # Move the long-running task to a separate thread
        entry.delete(0, 'end')

if __name__ == "__main__":
    main()
