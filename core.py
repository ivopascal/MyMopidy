import threading
import websocket
import json
import ast
import time

###############################################################################


##
### TODO:
##

# handle inputs better. support various types of inputs:
# strings, integers, relative integers, integer ranges
# maybe return the type of input and the list of inputs ? 
#
# probably a better way to do that

###############################################################################

# server replies and the next message id
results = []
idNum   = 0

# all api methods in a dict of dicts
M = {}

M['tracklist'] = {
	'index' : 'core.tracklist.index', # tl_track, tlid
	'shuffle' : 'core.tracklist.shuffle', # start, end, None
	'get_tracks' : 'core.tracklist.get_tracks', # None
	'get_tl_tracks' : 'core.tracklist.get_tl_tracks', # None
	'get_length' : 'core.tracklist.get_length', # None
	'add' : 'core.tracklist.add', # at_position, uris
	'clear' : 'core.tracklist.clear', # None
	'slice' : 'core.tracklist.slice', # start, end
	'move' : 'core.tracklist.move', # start, end, to_position
	'filter' : 'core.tracklist.filter', # criteria (type=dict)
	'remove' : 'core.tracklist.remove', # criteria (type=dict)
	# EXAMPLE: 
	# filter({'tlid':[1,2,3]}), filter({'uri':'abc'})
	'next_track' : 'core.tracklist.next_track', # tl_track, None
	'previous_track' : 'core.tracklist.previous_track', # None
	'get_next_tlid' : 'core.tracklist.get_next_tlid', # None
	'get_previous_tlid' : 'core.tracklist.get_previous_tlid', # None
	'get_random' : 'core.tracklist.get_random', # None
	'set_random' : 'core.tracklist.set_random', # value
	'get_single' : 'core.tracklist.get_single', # None
	'set_single' : 'core.tracklist.set_single', # value
	'get_consume' : 'core.tracklist.get_consume', # None
	'set_consume' : 'core.tracklist.set_consume', # value
	'get_repeat' : 'core.tracklist.get_repeat', # None
	'set_repeat' : 'core.tracklist.set_repeat' # value
}

M['playback'] = {
	'play' : 'core.playback.play', # tl_track, tlid, None
	'stop' : 'core.playback.stop', # None
	'pause' : 'core.playback.pause', # None
	'resume' : 'core.playback.resume', # None
	'next' : 'core.playback.next', # None
	'previous' : 'core.playback.previous', # None
	'seek' : 'core.playback.seek', # time_position (millisecs)
	'get_time_position' : 'core.playback.get_time_position', # None
	'get_state' : 'core.playback.get_state', # None
	'get_current_track' : 'core.playback.get_current_track', # None
	'get_current_tlid' : 'core.playback.get_current_tlid', # None
	'get_stream_title' : 'core.playback.get_stream_title', # None
	'get_current_tl_track' : 'core.playback.get_current_tl_track' # None
}

M['mixer'] = {
	'get_volume' : 'core.mixer.get_volume', # None
	'set_volume' : 'core.mixer.set_volume', # volume (Int in [0..100])
	'get_mute' : 'core.mixer.get_mute', # None
	'set_mute' : 'core.mixer.set_mute' # mute (bool)
}

M['library'] = {
	'lookup' : 'core.library.lookup', # uris
	'refresh' : 'core.library.refresh', # None
	'get_images' : 'core.library.get_images', # uris
	'search' : 'core.library.search', # query, uris, exact (bool)
	# EXAMPLES:
	# Returns results matching 'a' in any backend
	# search({'any': ['a']})
	# Returns results matching artist 'xyz' in any backend
	# search({'artist': ['xyz']})
	# Returns results matching 'a' and 'b' and artist 'xyz' in any backend
	# search({'any': ['a', 'b'], 'artist': ['xyz']})
	# Returns results matching 'a' if within the given URI roots
	# "file:///media/music" and "spotify:"
	# search({'any': ['a']}, uris=['file:///media/music', 'spotify:'])
	# Returns results matching artist 'xyz' and 'abc' in any backend
	# search({'artist': ['xyz', 'abc']})
	'browse' : 'core.library.browse', # uri
}

M['playlists'] = {
	'save' : 'core.playlists.save', # playlist
	'create' : 'core.playlists.create', # name, uri_scheme (backend)
	'delete' : 'core.playlists.delete', # uri
	'refresh' : 'core.playlists.refresh', # uri_scheme (backend)
	'lookup' : 'core.playlists.lookup', # uri
	'get_items' : 'core.playlists.get_items', # uri
	'as_list' : 'core.playlists.as_list' # None
}

###############################################################################

# functions for the websocket app/connection
def onMessage(wsa, message):
	global results
	# appends reply to results list (string to dict conversion)
	results.append(ast.literal_eval(message))
def onError(wsa, error):
	print("\n", error)
def onOpen(wsa):
	pass
def onClose(wsa):
	pass

# this is the websocket connection (not started yet)
wsa = websocket.WebSocketApp(
	url='ws://localhost:6680/mopidy/ws',
	on_message=onMessage,
	on_error=onError,
	on_open=onOpen,
	on_close=onClose
)

# this class is needed to do threads
class wsaThread(threading.Thread):
	def __init__(self, name, wsa):
		# this "super" call is also needed
		threading.Thread.__init__(self)
		self.name = name
		self.wsa = wsa
	# as well as this run function
	def run(self):
		print("Starting", self.name)
		# start the websocket connection
		self.wsa.run_forever()
		print("Exiting", self.name)

###############################################################################

# gets user input, split into command and args
def getInput(string=None):
	if not string:
		inp = input("{O}>> ")
	else:
		inp = input(string)
	inp = inp.split()
	command = inp[0]
	args = inp[1:]
	return (command, args)

# sets the volume. can deal with relative input like -10
def setVolume(arg=[]):
	if not arg:
		print("Current volume:", send(method=M['mixer']['get_volume']))
		return
	arg = arg[0]

	relative = 0
	if arg.startswith("+"):
		relative = 1
		arg = arg[1:]
	elif arg.startswith("-"):
		relative = -1
		arg = arg[1:]

	try:
		arg = int(arg)
	except ValueError:
		print("Invalid input...")
		return

	if not relative:
		newVol = arg
	else:
		currentVol = send(method=M['mixer']['get_volume'])
		newVol = currentVol + relative * arg
	if newVol > 100:
		newVol = 100
		print("Volume at maximum")
	if newVol < 0:
		newVol = 0
		print("Volume muted")
	send(timeout=0, method=M['mixer']['set_volume'], volume=newVol)

# returns a suitable json msg and the corresponding id num
def composeMessage(**kwargs):
	global idNum
	method = kwargs['method']
	del kwargs['method']
	json_msg = {
		'jsonrpc': '2.0',
		'id': idNum,
		'method': method,
		'params': kwargs
	}
	idNum += 1
	return (json.dumps(json_msg), idNum-1)

# sends the message and returns the reply if needed
def send(getReply=1, timeout=3, suppressError=False, **kwargs):
	(message, idNum) = composeMessage(**kwargs)
	wsa.send(message)
	if not timeout:
		# not interested in a reply
		return
	global results
	timeout *= 10
	if getReply:
		while timeout:
			for i in range(len(results)):
				if 'id' in results[i] and results[i]['id'] == idNum:
					if 'result' not in results[i]:
						print(results[i])
						print("No result received from mopidy...")
						return None
					return results[i]['result']
			time.sleep(0.1)
			timeout -= 1
		if not suppressError:
			print("Server took too long to respond...")
	else:
		# reset results sometimes to prevent slowdown over time
		results = []

###############################################################################
