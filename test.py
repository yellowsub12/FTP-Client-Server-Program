import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

max_buffer_size = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

print(max_buffer_size)
