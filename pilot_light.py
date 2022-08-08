import subprocess
import os

import json
sys_info = json.load(open("sys_info.json", "r"))
base_directory = sys_info["base_directory"]

def create():

	driver = subprocess.Popen(["python", "driver.py"])

	if platform.system() == "Windows":
		keyboard = subprocess.Popen(["python", os.path.join(base_directory, "keyboard_listener.py")])
	else:
		keyboard = subprocess.Popen(["sudo", "python", os.path.join(base_directory, "keyboard_listener.py")])

	return driver, keyboard

def shutdown(*processes):

	for p in processes:

		p.kill()

def main():

	driver, keyboard = create()

	try:
		while True:

			command = input("Enter command: ")

			if command == "restart":

				shutdown(driver, keyboard)

				driver, keyboard = create()

			elif command == "quit":

				#shutdown(driver, keyboard)

				break

	except KeyboardInterrupt:
		pass

	shutdown(driver, keyboard)

if __name__ == "__main__":

	main()