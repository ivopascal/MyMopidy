from core import send, M, getInput
from search import search
from printing import printIndex

###############################################################################


##
### TODO:
##

# add move functionality, eg: move [2-4] 8
# would move songs from index 2-4 after index 8
# handle input better --> core

###############################################################################


def editTracklist():
	while True:
		# show (part of) tracklist
		editor = showTracklist()
		if not editor:
			return None

		# get input + optional arguments
		(option, args) = getInput("What to do? ")

		# done
		if option in ["done", "quit", "return"]:
			return

		# remove from tracklist (add possibility to specify multiple tracks)
		if option in ["delete", "del", "remove"]:
			try:
				if args:
					selection = int(args[0])
				else:
					selection = int(input("Which one? "))
			except ValueError:
				print("Input argument must be an int, try again")
				continue
			editor.remove(selection)

		# to add, just search
		if option in ["add", "search", "find"]:
			search_terms = None
			position = None
			try:
				if args:
					position = int(args[0])
			except ValueError:
				if args:
					search_terms = args
			editor.add(search_terms=search_terms, position=position)

		# add functionality to move songs around
		if option in ["change", "move", "order"]:
			print("Not implemented yet")

def showTracklist():
	tracklist = send(method=M['tracklist']['get_tl_tracks'])
	editor = tracklistEditor(tracklist)
	editor.show()
	return editor

# manages the tracklist
class tracklistEditor():
	def __init__(self, tracklist):
		if not tracklist:
			print("Tracklist empty?")
			return None
		else:
			self.tracks = []
			track = dict()
			for i in range(len(tracklist)):
				track['index'] = i
				track['tlid'] = tracklist[i]['tlid']
				track['name'] = tracklist[i]['track']['name']
				track['artist'] = tracklist[i]['track']['artists'][0]['name']
				self.tracks.append(track)
				track = dict()

	def remove(self, index):
		current = send(timeout=2, suppressError=True, method=M['tracklist']['index'])
		if index == current:
			print("Can't remove currently playing track...")
		else:
			tlid = self.tracks[index]['tlid']
			send(method=M['tracklist']['remove'], criteria={'tlid':[tlid]})

	def add(self, search_terms=None, position=None):
		if position is None:
			# by default, "play next" which is at current index + 1
			position = send(timeout=2, method=M['tracklist']['index']) + 1
		search(search_terms=search_terms, adding=True, position=position)

	def show(self):
		print(len(self.tracks), "tracks in total.")
		current = send(timeout=2, suppressError=True, method=M['tracklist']['index'])
		if current == None:
			print("Couldn't find currently playing...")
			current = 0
		tlsize = len(self.tracks)
		start = 0
		end = tlsize
		# if the tracklist has more than 15 tracks then show the 5 last,
		# and the 10 next songs in the tracklist
		if tlsize > 15:
			start = current-5
			end = current+11
			if start < 0:
				end += abs(start)
				start = 0
			if end > tlsize:
				start -= (end - tlsize)
				end = tlsize
			if start > 0:
				print("...")
		for i in range(start, end):
			printIndex(i, current)
			print(self.tracks[i]['name'], "-", 
				  self.tracks[i]['artist'])
		if end < tlsize:
			print("...")
