import subprocess
import os

python_exe = os.path.join("C:", "Users", "David", "Anaconda3", "python.exe")
clown_folder = os.path.join("C:", "Users", "David", "Documents", "Programming", "clown_bot")

def create():

	driver = subprocess.Popen(["python", "driver.py"])

	keyboard = subprocess.Popen(["python", "keyboard_listener.py"])

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