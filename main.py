import time
import sys
from core import send, M, wsa, wsaThread, getInput
from playlists import playPlaylist
from tracklist import editTracklist, showTracklist
from search import search

###############################################################################


##
### TODO:
##

# volume controls
# show contents of a playlist
# search adds song to playlist --> current song restarts
# google search only works with a single search term?
# add multipliers for commands like next (eg: next 3)
# be able to pick more than one song from search
# be able to pick songs even if artist is searched

# 	options
# get state of options (random etc)
# both set/get random and set/get consume dont work
# options must be handled differently?



###############################################################################

# makes the thread
thread = wsaThread("Websocket Thread", wsa)
# this means the thread will stop when the main program stops
thread.daemon = True
# starts the threads
thread.start()
# wait for thread+connection to open
time.sleep(0.5)

###############################################################################

manual =  {
	"clear" : "Clears the tracklist including the currently playing song",
	"play" : "Play tracklist",
	"pause" : "Pause tracklist",
	"tracklist" : "Show the current tracklist",
	"edit" : "Goes into the tracklist edit loop. Currently supports remove (int) and add via search"
	"next (int)" : "Play the next song in the tracklist (times x)",
	"prev/previous (int)" : "Play the previous song in the tracklist (times x)",
	"playlist" : "Play a playlist via user input (takes optional search term).",
	"search" : "Searches via user input (takes optional search term).",
	"random" : "Toggles random (takes arguments to toggle) NOT WORKING",
	"exit/quit" : "Exits the script."
}

if len(sys.argv) > 1 and sys.argv[1] == '-s':
	speechCommand()
else:
	while(True):
		(command, args) = getInput()
		if command == "consume":
			# this is not working... 
			print(send(method=M['tracklist']['get_consume']))
			print(send(method=M['tracklist']['set_consume'], timeout=5, value=True))

		if command == "clear":
			send(getReply=0, method=M['tracklist']['clear'])

		if command == "play":
			send(getReply=0, method=M['playback']['play'])

		if command == "pause":
			send(getReply=0, method=M['playback']['pause'])

		if command in ["edit", "change", "remove"]:
			editTracklist()

		if command == "tracklist":
			showTracklist()

		if command == "next":
			if args:
				try:
					count = int(args[0])
					for i in range(count):
						send(getReply=0, method=M['playback']['next'])
						time.sleep(0.1)
				except ValueError:
					print("Input argument must be an int, try again")
			else:
				send(getReply=0, method=M['playback']['next'])

		if command in ["prev", "previous"]:
			if args:
				try:
					count = int(args[0])
					for i in range(count):
						send(getReply=0, method=M['playback']['previous'])
						time.sleep(0.1)
				except ValueError:
					print("Input argument must be an int, try again")
			else:
				send(getReply=0, method=M['playback']['previous'])

		if command == "playlist":
			playPlaylist(args)

		if command == "search":
			search(args)

		# this is not working...
		if command == "random":
			if args:
				if args[0].lower() in ["on", "yes", "true"]:
					send(getReply=0, method=M['tracklist']['set_random'], value=True)
				if args[0].lower() in ["off", "no", "false"]:
					send(getReply=0, method=M['tracklist']['set_random'], value=False)
			else:
				print(send(method=M['tracklist']['get_random']))

		if command in ["options", "help", "?", "man"]:
			for k,v in manual.items():
				print(k, "-", v)

		if command in ["exit", "quit"]:
			wsa.close()
			time.sleep(0.5)
			break

###############################################################################

# listen and return spoken text
def getText(r, mic):
	with mic as source:
		audio = r.listen(source)
	return r.recognize_google(audio)

# test function just plays a song
def playSong():
	uris = ["spotify:track:460uwjOb9e0275u5dtgmCf"]
	send(getReply=0, method=M['tracklist']['clear'])
	send(method=M['tracklist']['add'], uris=uris)
	send(getReply=0, method=M['playback']['play'])

# test function to show speech command
def speechCommand():
	import speech_recognition as sr
	r = sr.Recognizer()
	mic = sr.Microphone()
	text = getText(r, mic)
	print(text)
	if text == "play song":
		playSong()
	time.sleep(3)

# maybe its a better idea to use the google voice kit

###############################################################################















# check out how the setter function works



'''
	# toggles volume
	@staticmethod
	def command_on_off(args, getter, setter):
		if args:
			if args[0].lower() in {'on', 'yes', 'true'}:
				new_value = True
			elif args[0].lower() in {'off', 'no', 'false'}:
				new_value = False
		else:
			current_value = getter(timeout=15)
			new_value = not current_value

		setter(new_value)

	# sets volume
	@staticmethod
	def command_numeric(args, getter, setter, callback=None, step=1, res=1):
		if args:
			arg_value = args[0]
			current_value = 0

			relative = +1 if arg_value.startswith('+') \
				else -1 if arg_value.startswith('-') \
				else 0

			if relative:
				current_value = getter(timeout=15)
				arg_value = arg_value[1:]
			else:
				relative = 1

			if unicode(arg_value).isnumeric():
				step = int(arg_value)
			elif arg_value:
				return

			new_value = current_value + step * relative * res
			new_value = max(new_value, 0)
			setter(new_value)
		else:
			# No argument, get current value
			getter(on_result=callback)

'''