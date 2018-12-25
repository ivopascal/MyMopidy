import time
import sys
from core import send, M, wsa, wsaThread, getInput, setVolume
from playlists import playPlaylist
from tracklist import editTracklist, showTracklist
from search import search

###############################################################################


##
### TODO:
##

# conform to PEP8
#
# rework the websocket connection. better error handling, retry
# connection on failt, better handling of results, etc

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
	"shuffle" : "Shuffles the tracklist order",
	"play" : "Play tracklist",
	"pause" : "Pause tracklist",
	"vol ((int))" : "Shows current volume, or changes it. Can also do relative inputs like \"-10\"",
	"tracklist ((\"all\"))" : "Show the current tracklist. If \"all\" is given, shows everything",
	"next ((int))" : "Play the next song in the tracklist (times x)",
	"prev ((int))" : "Play the previous song in the tracklist (times x)",
	"playlist" : "Play a playlist via user input (takes optional search term) (needs \"play\" afterwards)",
	"search" : "Searches via user input (takes optional search term).",
	"exit/quit" : "Exits the script.",

	"edit" : "Goes into the tracklist edit loop.",
	"edit: show" : "Shows entire tracklist",
	"edit: add ((int)) ((search term))" : "Adds a song at optional position x with optional search term, by default \"play next\"",
	"edit: remove (int)" : "Removes the song at position x",
	"edit: move (int) (int) ((int))" : "Moves the song(s) at x (or from x to y, excluding y) to (after) position z"
}

if len(sys.argv) > 1 and sys.argv[1] == '-s':
	speechCommand()
else:
	while(True):
		(command, args) = getInput()
		if command in ["vol", "volume"]:
			setVolume(args)

		if command == "clear":
			send(getReply=0, method=M['tracklist']['clear'])

		if command in ["shuffle", "random", "rand"]:
			send(getReply=0, method=M['tracklist']['shuffle'])

		if command == "play":
			send(getReply=0, method=M['playback']['play'])

		if command == "pause":
			send(getReply=0, method=M['playback']['pause'])

		if command in ["edit", "change", "remove"]:
			editTracklist()

		if command == "tracklist":
			if args and args[0] == "all":
				showTracklist(showAll=True)
			else:
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

		if command in ["options", "help", "?", "man"]:
			index = 0
			for k,v in manual.items():
				print(index, ")", k, "-", v)
				index += 1

		if command in ["exit", "quit"]:
			wsa.close()
			time.sleep(0.5)
			break

###############################################################################

# simple proof of concept. leave this for much later

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

###############################################################################