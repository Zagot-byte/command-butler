#!/usr/bin/env python3
import socket
import sys
import json

SOCKET_PATH = "/run/command-butler/butler.sock"

if len(sys.argv) < 2:
    print("Usage: butler <intent>")
    sys.exit(1)

intent = " ".join(sys.argv[1:])

client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client.connect(SOCKET_PATH)

client.sendall(json.dumps({"input": intent}).encode())

response = client.recv(4096)
print(response.decode())

client.close()

