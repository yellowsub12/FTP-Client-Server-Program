# Ali Turkman 40111059
# This is my original work.
# The function of this file was to determine the size of the internal buffer of the socket, a value which is decided by the OS.

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

max_buffer_size = s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

print(max_buffer_size)
