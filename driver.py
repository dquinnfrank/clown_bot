import sys

import datetime
import keyboard
import json
import os

import asyncio
import discord
from discord.ext import commands
from discord import ChannelType

import sounds

# This should be placed into a class
import pyttsx3
from io import BytesIO

import sys
sys.path.append(os.path.join("C:","Users","David","Anaconda3","pkgs","ffmpeg-4.3.1-ha925a31_0","Library","bin"))

def find_target(voice_channels, target):

	for v in voice_channels:
		for m in v.voice_states.keys():
			print(m)
			if str(m) == target.strip("<@> "):
				return v

	return None

class clown_bot(discord.Client):

	def __init__(self, target_channel, *args, sound_maker = None, command_channel = "bot-pit", **kwargs):

		if sound_maker is None:
			self.sound_maker = sounds.noise_maker_composite.basic_pair()
		else:
			self.sound_maker = sound_maker

		self.target_channel = target_channel
		self.command_channel = command_channel

		self.sound_dead_zone = 15
		self.last_message_time = datetime.datetime.utcnow() - datetime.timedelta(seconds = self.sound_dead_zone)

		super().__init__(*args, **kwargs)

	async def on_ready(self):

		print("Logged in as {}".format(self.user))

	async def on_message(self, message):

		if message.author == self.user:
			return
	 
		print("Message content: {}".format(message.content))
		print("Message from: {}".format(message.author))
		print("In channel: {}".format(message.channel.name))
		print("At time: {}".format(message.created_at))
		print("Current time: {}".format(datetime.datetime.utcnow()))

		if message.channel.name == self.target_channel:
			print("Speak the truth")

			await self.sound_maker.add_sound(message.content, "tts")

			if "clown" in message.content:
				print("clowning")

				await self.sound_maker.add_sound("clown", "sounds", timestamp = message.created_at)

			await self.sound_maker.play_all()

		# This should be done with commands, but I don't want to figure it out
		elif (message.channel.name == self.command_channel) and (message.content[0] == "$"):

			message = message.content[1:]
			command, content = message.split(" ", maxsplit = 1)

			if command == "clown":

				print("clowning: {}".format(content.strip()))

				voice_channels = list([x for x in self.get_all_channels() if x.type == ChannelType.voice])
				#print(voice_channels)

				# Find the target
				found_channel = find_target(voice_channels, content)

				if found_channel is not None:
					print(dir(found_channel))

					options = ["did you know that the annual salary of a clown is $50,000? So why are you doing it for free?"]
					choosen = options[0]
					engine = pyttsx3.init()
					bytes_file = BytesIO()
					engine.save_to_file(choosen, bytes_file)
					engine.runAndWait()

					#clown_theme = self.sound_maker.queues["sounds"].sounds["clown"]
					#audio_source = discord.FFmpegPCMAudio(bytes_file.read())
					#audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(os.path.join("sound_assets", "entry_of_the_gladiators.mp3")))
					FFMPEG_OPTIONS = {'options': '-vn'}
					audio_source = discord.FFmpegPCMAudio("clown_phrase.mp3", **FFMPEG_OPTIONS)
					#audio_source = await discord.FFmpegOpusAudio.from_probe("entry_of_the_gladiators.opus")

					vc = await found_channel.connect()
					print(dir(vc))
					print(dir(vc.source))

					#player = vc.create_ffmpeg_player(bytes_file.read(), after=lambda: print('done'))
					#player.start()
					#vc.source.volume = 100
					vc.play(audio_source, after = lambda x: print("done playing"))
					while vc.is_playing():
						await asyncio.sleep(1)

					#vc.play(audio_source, after = None)
					await vc.disconnect()

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

def main():

	sound_maker = sounds.noise_maker_composite.basic_pair()

	input_listener = tcp_listener(sound_maker)

	clowner = clown_bot(target_channel = "shitomarsays", sound_maker = sound_maker)

	clowner.loop.create_task(input_listener.run())

	token = json.load(open(os.path.join("secrets", "token.json"), "r"))["token"]
	clowner.run(token)

if __name__ == "__main__":

	main()