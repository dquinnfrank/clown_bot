from abc import ABC, abstractmethod

import datetime
import json
import os

from collections import OrderedDict

import pydub
from pydub.playback import play
import pyttsx3

import asyncio

class noise_maker(ABC):
	"""
	Interface for classes that make noises
	"""

	@abstractmethod
	def __init__(self, sound_timeout = 15):
		pass

	@abstractmethod
	async def make_sound(self, sound):
		pass

	@abstractmethod
	async def add_sound(self, sound, timestamp = None):
		pass

	@abstractmethod
	async def play_next(self):
		pass

	@abstractmethod
	def is_empty(self):
		pass

class noise_maker_single(noise_maker):
	"""
	Manages a single noise making queue
	"""

	def __init__(self, sound_timeout = None, sound_deadzone = None):

		# The amount of time in seconds before a sound becomes stale
		# If None, no mercy
		self.sound_timeout = sound_timeout

		# The amount of time to wait before playing another sound
		# If None, no mercy
		self.sound_deadzone = sound_deadzone
		self.last_sound_played_time = None

		# This holds all of the sounds that have been queued up as (timestamp, sound)
		self.sound_queue = asyncio.PriorityQueue()

		# This tracks if the player should be running
		self.mute = False

	async def set_mute(self, mute):

		self.mute = mute

	async def get_mute(self):

		return self.mute

	async def add_sound(self, sound, timestamp = None):
		"""
		Adds a sound to the queue
		sound : the name of the sound to play
		"""

		if timestamp is None:
			timestamp = datetime.datetime.utcnow()

		self.sound_queue.put_nowait((timestamp, sound))

	async def play_next(self):
		"""
		Play the next valid sound
		"""

		try:

			# Get the oldest sound
			next_sound_item = self.sound_queue.get_nowait()

		# No items in queue, do nothing
		except asyncio.QueueEmpty:
			pass

		# Something to play
		else:

			next_sound_time = next_sound_item[0]
			next_sound = next_sound_item[1]
			current_time = datetime.datetime.utcnow()

			print("play_next current_time: {}".format(current_time))
			print("play_next next_sound_time: {}".format(next_sound_time))

			# Current time can appear before item time due to clock differences, if it does set it to the item time
			current_time = current_time if current_time > next_sound_time else next_sound_time

			# Check for stale sounds
			if self.sound_timeout is None:
				stale = False

			else:
				seconds_passed = (current_time - next_sound_time).seconds
				stale = seconds_passed > self.sound_timeout

			# No sounds have been played yet
			if self.last_sound_played_time is None or self.sound_deadzone is None:
				in_deadzone = False

			# Check for sound played too recently
			else:
				seconds_passed_since_last_sound = (current_time - self.last_sound_played_time).seconds
				in_deadzone = seconds_passed_since_last_sound < self.sound_deadzone

			print("queue: {}".format(self.__class__.__name__))
			print("Sound: {}".format(next_sound))
			print("mute: {}, stale: {}, deadzone : {}".format(self.mute, stale, in_deadzone))

			# To prevent spamming, only check the sound if it is recent and no other sound has been played recently
			if not self.mute and not in_deadzone and not stale:

				await self.make_sound(next_sound)

				self.last_sound_played_time = current_time

			self.sound_queue.task_done()

	async def play_all(self):
		"""
		Play all valid sounds in the queue. Some items may timeout while playing
		"""

		while not self.is_empty():

			await self.play_next()

	def is_empty(self):
		return self.sound_queue.empty()

class noise_maker_composite:
	"""
	Manages multiple noisemaking queues
	"""

	def __init__(self, queues):
		"""
		queues : {"name" : queue_name, "priority" : 0, "queue" : queue_object}
		"""

		if len(queues) == 0:
			raise ValueError("Need at least 1 queue")

		# Save a dictionary that matches priorities to queue names
		self.priorities = OrderedDict()
		for item in sorted(queues, key = lambda x: x["priority"]):
			self.priorities[item["priority"]] = item["name"]

		# Saves a dictionary matching names to queue objects
		self.queues = {x["name"] : x["queue"] for x in queues}

		# Tracks if the player should be making noise
		self.mute = False

	@classmethod
	def basic_pair(cls, sound_config = os.path.join("configs", "clown_sounds.json"), sound_timeout = 10, sound_deadzone = 20):
		"""
		Class constructor that will quickly create one tts and one sound maker
		"""

		sound_queue = sound_file_player.from_json(sound_config, sound_timeout = sound_timeout, sound_deadzone = sound_deadzone)
		tts_queue = text_to_speech_player(sound_timeout = 30)

		return cls([{"priority" : 1, "name" : "tts", "queue" : tts_queue}, {"priority" : 2, "name" : "sounds", "queue" : sound_queue}])

	async def set_mute(self, mute):

		self.mute = mute

		for priority, queue_name in self.priorities.items():

			await self.queues[queue_name].set_mute(self.mute)

	async def get_mute(self):

		return self.mute

	async def add_sound(self, sound, queue_name, timestamp = None):
		"""
		Adds a sound the the correct queue
		sound : sound name
		queue_name : the queue the sound belongs to
		"""

		await self.queues[queue_name].add_sound(sound, timestamp = timestamp)

	async def play_next(self):
		"""
		Plays the next valid sound
		"""

		for priority, queue_name in self.priorities.items():

			queue = self.queues[queue_name]

			if not queue.is_empty():

				await queue.play_next()
				break

	async def play_all(self):
		"""
		Play all valid sounds in the queue. Some items may timeout while playing
		"""

		while not self.is_empty():

			await self.play_next()

	def is_empty(self):
		return all([x.is_empty() for x in self.queues.values()])

class sound_file_player(noise_maker_single):
	"""
	Plays clips from sound files
	"""

	def __init__(self, sounds, **kwargs):

		if len(sounds) == 0:
			raise ValueError("sounds must have at least one sound")

		kwargs["sound_timeout"] = kwargs.get("sound_timeout", 15)

		super().__init__(**kwargs)

		self.sounds = sounds

	@classmethod
	def from_json(cls, config_file_name, **kwargs):
		"""
		Uses a json file to configure the sounds
		"""

		with open(config_file_name, "r") as f:
			configs = json.load(f)

		sounds = {}
		for item in configs:

			# Load the full sound
			file_name = os.path.join(*item["file_name"])
			full_sound = pydub.AudioSegment.from_file(file_name)

			# If start and end are present, extract the clip
			if "start" in item:
				millisecond_const = 1000
				sound_clip = full_sound[item["start"] * millisecond_const : item["end"] * millisecond_const]

			else:
				sound_clip = full_sound

			# Save the sound
			sounds[item["name"]] = sound_clip

		return cls(sounds, **kwargs)

	async def make_sound(self, sound): 
		"""
		Plays the specified sound
		"""

		sound_clip = self.sounds[sound]
		pydub.playback.play(sound_clip)

class text_to_speech_player(noise_maker_single):
	"""
	Plays text to speech
	"""

	def __init__(self, **kwargs):

		super().__init__(**kwargs)

		self.engine = pyttsx3.init()

	async def make_sound(self, sound):
		"""
		Reads the sent text
		"""

		self.engine.say(sound)
		self.engine.runAndWait()

async def test_clips():

	clips = sound_file_player.from_json(os.path.join("configs", "clown_sounds.json"), sound_timeout = 2)

	await clips.add_sound("clown")
	time.sleep(1)
	await clips.play_next()
	print("done")

async def test_tts():

	tts = text_to_speech_player()

	await tts.add_sound("Clown world vision activated. Nothing changed.")
	await tts.play_next()

if __name__ == "__main__":

	start_time = datetime.datetime.now()
	asyncio.run(test_tts())
	end_time = datetime.datetime.now()
	print(end_time - start_time)