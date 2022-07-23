import keyboard

import socket

target_host = '127.0.0.1'
target_port = 8888

def send_tcp(message):

	print("Sending message: {}".format(message))

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((target_host,target_port))

	client.send(message.encode())

	client.close()

keyboard.add_hotkey("ctrl+alt+j", send_tcp, args = ("ctrl+alt+j",))
keyboard.add_hotkey("ctrl+alt+k", send_tcp, args = ("ctrl+alt+k",))
#keyboard.add_hotkey("ctrl+alt+l", send_tcp, args = ("ctrl+alt+l",))
keyboard.wait()
