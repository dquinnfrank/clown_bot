import sys

import datetime
import keyboard
import json
import os
import platform
import random

import argparse

import asyncio
import discord
from discord.ext import commands
from discord import ChannelType

import sounds

import subprocess

# This should be placed into a class
import pyttsx3
from io import BytesIO

sys_info = json.load(open("sys_info.json", "r"))
base_directory = sys_info["base_directory"]

#intents = discord.Intents.default()
#intents.message_content = True

#TODO: move this to a shared util
def find_target(voice_channels, target):

	for v in voice_channels:
		for m in v.voice_states.keys():
			#print(m)
			if str(m) == target.strip("<@> "):
				return v

	return None

class clown_bot(discord.Client):

	def __init__(self, *args, target_channel = None, target_user = None, sound_maker = None, discord_sound_maker = None, command_channel = None, **kwargs):

		intents = discord.Intents.default()
		intents.members = True
		intents.message_content = True

		if sound_maker is None:
			self.sound_maker = sounds.noise_maker_composite.basic_pair()
		else:
			self.sound_maker = sound_maker

		if discord_sound_maker is None:
			self.discord_sound_maker = sounds.discord_noise_maker(self, sound_timeout = 10, sound_deadzone = 20)
		else:
			self.discord_sound_maker = discord_sound_maker

		# TODO: save these configs externally
		self.target_channel = target_channel or "shitomarsays"
		self.target_user = target_user or "168605217858781186"
		self.command_channel = command_channel or "bot-pit"

		self.sound_dead_zone = 15
		self.last_message_time = datetime.datetime.utcnow() - datetime.timedelta(seconds = self.sound_dead_zone)

		super().__init__(*args, intents = intents, **kwargs)

	async def setup_hook(self):

		input_listener = tcp_listener(self.sound_maker)

		self.loop.create_task(input_listener.run())

	async def on_ready(self):

		print("Logged in as {}".format(self.user))

	async def on_message(self, message):

		if message.author == self.user:
			return

		voice_channels = list([x for x in self.get_all_channels() if x.type == ChannelType.voice])
	 
		print("Message content: {}".format(message.content))
		print("Message from: {}".format(message.author))
		print("In channel: {}".format(message.channel.name))
		print("At time: {}".format(message.created_at))
		print("Current time: {}".format(datetime.datetime.now(datetime.timezone.utc)))

		if message.channel.name == self.target_channel:

			# Check for target in discord
			if find_target(voice_channels, self.target_user) is not None:

				print("Speak the truth")

				await self.sound_maker.add_sound(message.content, "tts")

				if "clown" in message.content.lower():
					print("clowning")

					await self.sound_maker.add_sound("clown", "sounds", timestamp = message.created_at)

				await self.sound_maker.play_all()

		# This should be done with commands, but I don't want to figure it out
		elif (message.channel.name == self.command_channel) and (message.content[0] == "$"):

			message_text = message.content[1:]
			command, content = message_text.split(" ", maxsplit = 1)

			if command == "clown":

				print("clowning: {}".format(content.strip()))

				await self.discord_sound_maker.add_sound(message, timestamp = message.created_at)

				await self.discord_sound_maker.play_all()

class tcp_listener():

	def __init__(self, sound_maker):

		self.sound_maker = sound_maker

	@staticmethod
	async def on_incoming_tcp(cls, reader, writer):
		data = await reader.read(100)
		message = data.decode()
		addr = writer.get_extra_info('peername')

		print(f"Received {message!r} from {addr!r}")
		writer.close()

		if message == "ctrl+alt+j":
			await cls.sound_maker.add_sound("clown", "sounds")
			await cls.sound_maker.play_all()

		elif message == "ctrl+alt+k":

			current_mute = await cls.sound_maker.get_mute()

			if current_mute:

				await cls.sound_maker.set_mute(False)

				await cls.sound_maker.add_sound("Clown world vision activated. Nothing changed", "tts")
				await cls.sound_maker.play_all()

			else:

				await cls.sound_maker.add_sound("You cannot hide from clown world forever", "tts")
				await cls.sound_maker.play_all()

				await cls.sound_maker.set_mute(True)

		elif message == "ctrl+alt+l":
			#print("shutting down")
			#raise KeyboardInterrupt
			pass

	async def run(self):

		self.server = await asyncio.start_server(
			lambda reader, writer: self.on_incoming_tcp(self, reader, writer), '127.0.0.1', 8888)

		addrs = ', '.join(str(sock.getsockname()) for sock in self.server.sockets)
		print(f'Serving on {addrs}')

		async with self.server:
			await self.server.serve_forever()

def main(**kwargs):

	sound_maker = sounds.noise_maker_composite.basic_pair()

	#input_listener = tcp_listener(sound_maker)

	clowner = clown_bot(**kwargs)

	#clowner.loop.create_task(input_listener.run())

	if platform.system() == "Windows":
		keyboard = subprocess.Popen(["python", "keyboard_listener.py"])
	else:
		keyboard = subprocess.Popen(["sudo", "python", "keyboard_listener.py"])

	try:
		token = json.load(open(os.path.join("secrets", "token.json"), "r"))["token"]
		clowner.run(token)
	except:
		pass
	finally:
		print("Shutting down")
		keyboard.kill()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = "Only begun, the clown wars have")

	parser.add_argument("--target_channel", "-c",
                    default = None,
                    help = "The channel to watch for things to quote")
	parser.add_argument("--target_user", "-u",
                    default = None,
                    help = "The person to harass in target_channel")
	parser.add_argument("--command_channel", "-o",
                    default = None,
                    help = "The channel to watch for bot commands")

	kwargs = vars(parser.parse_args())

	main(**kwargs)